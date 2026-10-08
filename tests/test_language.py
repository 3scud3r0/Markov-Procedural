import json
from pathlib import Path
import unittest
import subprocess
import tempfile
from markovjunior.language import Session, Runtime, Budget

ROOT = Path(__file__).resolve().parents[1]


class LanguageTests(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def run_program(self, source, **options):
        return self.session.execute({'schema': 'markov.project/1', 'seed': 42,
            'entry': 'main.mp', 'files': [{'name': 'main.mp', 'content': source}], **options})

    def test_general_programming_classes_recursion_imports_and_exact_integers(self):
        result = self.run_program('''from collections import Counter
class Algorithm:
    def factorial(self, n):
        return 1 if n < 2 else n * self.factorial(n - 1)
values = [Algorithm().factorial(n) for n in range(25)]
assert values[-1] == 620448401733239439360000
print(Counter("procedural"))
emit("values.json", values)
''')
        self.assertTrue(result['ok'], result['error'])
        self.assertIn('Counter', result['stdout'])
        self.assertEqual(json.loads(result['files'][0]['content'])[-1], 620448401733239439360000)

    def test_multifile_imports_and_module_sources_are_refreshed(self):
        project = {'schema': 'markov.project/1', 'seed': 42, 'files': [
            {'name': 'main.mp', 'content': 'from helper import value\nprint(value())'},
            {'name': 'helper.mp', 'content': 'def value():\n    return 17'}]}
        a = self.session.execute(project)
        self.assertEqual(a['stdout'], '17\n')
        project['files'][1]['content'] = 'def value():\n    return 29'
        b = self.session.execute(project)
        self.assertEqual(b['stdout'], '29\n')

    def test_procedural_api_import_rule_and_geometry(self):
        result = self.run_program('''from markov import *
@rule
def spawn(n):
    return [sphere(radius=0.2, position=[i, 1, 0]) for i in range(n)]
nodes = spawn(3)
nodes[0].translate(y=2).rotate(y=0.5).resize(2)
scene.background = "#222233"
emit("ids.json", [n.id for n in nodes])
''')
        self.assertTrue(result['ok'], result['error'])
        self.assertEqual(result['rules'], ['spawn'])
        self.assertEqual(result['scene']['objects'][0]['position'], [0, 3, 0])
        self.assertEqual(result['scene']['objects'][0]['scaling'], [2, 2, 2])

    def test_project_packages_and_relative_imports(self):
        result = self.session.execute({'schema': 'markov.project/1', 'files': [
            {'name': 'main.mp', 'content': 'from package import value\nprint(value())'},
            {'name': 'package/__init__.mp', 'content': 'from .helper import value'},
            {'name': 'package/helper.mp', 'content': 'def value():\n    return 47'}]})
        self.assertTrue(result['ok'], result['error'])
        self.assertEqual(result['stdout'], '47\n')

    def test_deterministic_random_noise_and_grammar(self):
        source = '''points = [random(-5,5) for _ in range(8)]
emit("data.json", {"points": points, "noise": noise(0.7, 1.1),
                  "text": grammar({"start": ["a", "b", "c"]})})'''
        a = self.run_program(source)
        b = self.run_program(source)
        self.assertEqual(a['files'], b['files'])
        self.assertNotEqual(a['files'], self.run_program(source, seed=99)['files'])
        rng = Runtime()
        self.assertAlmostEqual(rng.noise(1 - 1e-6, 2), rng.noise(1 + 1e-6, 2), places=5)

    def test_parameters_create_metadata_and_overrides_are_validated(self):
        source = 'n=param("n",3,min=1,max=10,step=1)\nprint(n)'
        result = self.run_program(source, parameters={'n': 7})
        self.assertEqual(result['stdout'], '7\n')
        self.assertEqual(result['parameters'][0]['value'], 7)
        self.assertFalse(self.run_program(source, parameters={'n': 11})['ok'])

    def test_animation_preserves_variables_and_keyboard_state(self):
        result = self.run_program('''node = sphere()
def update(t, dt):
    node.position[0] += dt * (2 if "ArrowRight" in keys else 1)
''')
        self.assertTrue(result['animation'])
        a = self.session.frame(1, .5, {'keys': ['ArrowRight']})
        self.assertEqual(a['scene']['objects'][0]['position'][0], 1)
        b = self.session.frame(2, .5)
        self.assertEqual(b['scene']['objects'][0]['position'][0], 1.5)

    def test_runtime_and_syntax_errors_report_user_file_and_line(self):
        error = self.run_program('print("before")\nx = 1 / 0')['error']
        self.assertEqual((error['file'], error['line'], error['type']), ('main.mp', 2, 'ZeroDivisionError'))
        error = self.run_program('def broken(:\n    pass')['error']
        self.assertEqual((error['file'], error['line'], error['type']), ('main.mp', 1, 'SyntaxError'))

    def test_imported_file_error_has_correct_location(self):
        result = self.session.execute({'schema': 'markov.project/1', 'files': [
            {'name': 'main.mp', 'content': 'from helper import broken\nbroken()'},
            {'name': 'helper.mp', 'content': 'def broken():\n    return unknown_value'}]})
        self.assertEqual((result['error']['file'], result['error']['line']), ('helper.mp', 2))

    def test_budget_terminates_a_nonterminating_python_loop(self):
        with self.assertRaises(TimeoutError):
            with Budget(seconds=1, lines=100):
                exec(compile('while True:\n    pass', 'loop.mp', 'exec'), {})

    def test_mesh_validation_and_scene_limits(self):
        runtime = Runtime()
        with self.assertRaises(ValueError): runtime.mesh([[0, 0, 0]] * 3, [[0, 1, 9]])
        with self.assertRaises(ValueError): runtime.sphere(radius=float('nan'))
        with self.assertRaises(ValueError): runtime.box(size=[1, -2, 3])
        mesh = runtime.mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
        self.assertEqual(mesh.geometry['faces'], [[0, 1, 2]])

    def test_files_can_be_created_using_emit_or_standard_python_io(self):
        result = self.run_program('emit("data.json", {"ok":True})\nwith open("ordinary.txt","w") as f:\n    f.write("hello")')
        self.assertTrue(result['ok'], result['error'])
        files = {f['name']: f for f in result['files']}
        self.assertEqual(json.loads(files['data.json']['content']), {'ok': True})
        self.assertEqual(files['ordinary.txt']['encoding'], 'base64')

    def test_invalid_projects_cannot_reuse_previous_session_state(self):
        self.run_program('sphere()')
        result = self.session.execute({'schema': 'unknown'})
        self.assertFalse(result['ok'])
        self.assertEqual(result['scene']['objects'], [])
        result = self.run_program('pass', files=[{'name': '../outside.mp', 'content': 'pass'}])
        self.assertFalse(result['ok'])

    def test_nine_existing_backends_are_accessible_from_programs(self):
        result = self.run_program('generate("program", targets=["python","javascript","typescript","c","cpp","rust","go","lua","sql"])')
        self.assertTrue(result['ok'], result['error'])
        self.assertEqual(len(result['files']), 9)

    def test_all_published_examples_are_executable(self):
        catalog = json.loads((ROOT / 'examples/language/catalog.json').read_text())
        for example in catalog:
            folder = ROOT / 'examples/language' / example['id']
            project = {'schema': 'markov.project/1', 'files': [
                {'name': p.name, 'content': p.read_text()} for p in folder.glob('*.mp')]}
            with self.subTest(example=example['id']):
                result = self.session.execute(project)
                self.assertTrue(result['ok'], result['error'])

    def test_cli_returns_failure_status_when_program_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'main.mp'
            source.write_text('raise ValueError("user program failed")')
            result = subprocess.run(['python', '-m', 'markovjunior', 'run', str(source),
                '--output', str(Path(temp) / 'output')], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('user program failed', result.stderr)
