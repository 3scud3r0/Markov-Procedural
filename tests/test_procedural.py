import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from markovjunior.procedural import (Artifact,Document,Context,Program,Function,Literal,Ref,Binary,Set,If,Repeat,Return,default_registry,run_project)
from markovjunior.procedural.generators import Grammar,program
from markovjunior.core import DotNetRandom

BASE=Path(__file__).resolve().parents[1]


class ProceduralTests(unittest.TestCase):
    def context(self,seed=42):return Context(seed,DotNetRandom(seed),BASE)

    def test_seed_changes_program_but_same_seed_is_identical(self):
        a=program({},self.context(42)).value
        self.assertEqual(a.to_data(),program({},self.context(42)).value.to_data())
        self.assertNotEqual(a.to_data(),program({},self.context(43)).value.to_data())

    def test_ir_round_trip_and_custom_program_recipe(self):
        ir=program({},self.context()).value
        exported=json.loads(json.dumps(ir.to_data()))
        loaded=Program.from_data(exported)
        self.assertEqual(loaded,ir)
        with tempfile.TemporaryDirectory() as temp:
            run_project({'version':1,'jobs':[{'name':'edited','generator':'program-ir','params':{'ir':exported},'targets':['c','rust','json']}]},temp)
            self.assertTrue((Path(temp)/'edited/edited.c').exists())
        exported['program']['node']='UnknownExecutable'
        with self.assertRaises(ValueError):Program.from_data(exported)

    def test_pipeline_order_and_targets_do_not_change_generation(self):
        job={'name':'source','generator':'program','params':{},'targets':['python','json']}
        other={'name':'story','generator':'grammar','params':{'rules':{'start':['ola','mundo']}},'targets':['text']}
        with tempfile.TemporaryDirectory() as temp:
            a,b=Path(temp)/'a',Path(temp)/'b'
            run_project({'version':1,'seed':42,'jobs':[job,other]},a,base=BASE)
            run_project({'version':1,'seed':42,'jobs':[other,{**job,'targets':['json','python','rust']}]},b,base=BASE)
            self.assertEqual((a/'source/source.py').read_bytes(),(b/'source/source.py').read_bytes())
            self.assertEqual((a/'source/source.json').read_bytes(),(b/'source/source.json').read_bytes())

    def test_recursive_grammar_finishes_and_escapes_literal_tags(self):
        g=Grammar({'start':[{'text':'a<start>','weight':100},'z']})
        text,trace=g.expand('<start>',DotNetRandom(42),max_depth=8)
        self.assertTrue(text.endswith('z'))
        self.assertLessEqual(len(trace),8)
        g=Grammar({'start':['\\<literal> <int:-3:3>']})
        text,_=g.expand('<start>',DotNetRandom(1))
        self.assertTrue(text.startswith('<literal> '))

    def test_grammar_detects_unproductive_and_undefined_rules(self):
        with self.assertRaisesRegex(ValueError,'undefined'):Grammar({'start':['<missing>']})
        with self.assertRaisesRegex(ValueError,'cannot finish'):Grammar({'start':['<start>']}).expand('<start>',DotNetRandom(42))
        with self.assertRaises(ValueError):Grammar({'start':[{'text':'x','weight':float('nan')}]})

    def test_grammar_character_budget_includes_builtin_values(self):
        with self.assertRaisesRegex(ValueError,'character budget'):
            Grammar({'start':['<int:1000:1000>']}).expand('<start>',DotNetRandom(42),max_chars=2)

    def test_ir_rejects_undefined_variables_and_unsafe_arithmetic(self):
        with self.assertRaisesRegex(ValueError,'undefined'):
            Program((Function('demo',('x',),(Return(Ref('unknown')),)),)).validate()
        with self.assertRaisesRegex(ValueError,'exact integer'):
            Program((Function('demo',('x',),(Return(Binary('*',Ref('x'),Literal(10**12))),)),)).validate()
        with self.assertRaises(ValueError):
            Program((Function('demo',('x',),(Repeat('x',2,()),Return(Ref('x')))),)).validate()

    def test_data_nested_schema_and_svg_are_structured_outputs(self):
        recipe=json.loads((BASE/'examples/procedural/project.json').read_text())
        recipe['jobs']=[j for j in recipe['jobs'] if j['generator'] in ('data','scene')]
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            manifest=run_project(recipe,out,base=BASE)
            svg=ET.parse(out/'jardim/jardim.svg').getroot()
            self.assertEqual(svg.tag,'{http://www.w3.org/2000/svg}svg')
            self.assertGreater(len(svg),100)
            data=json.loads((out/'entidades/entidades.json').read_text())['value']
            self.assertEqual(len(data),12)
            self.assertTrue(all(10<=row['energia']<=100 for row in data))
            self.assertEqual(len(manifest['jobs']),2)

    def test_generator_and_target_extension_are_executable(self):
        registry=default_registry()
        registry.load_plugin(BASE/'examples/procedural/extension.py')
        recipe=json.loads((BASE/'examples/procedural/extensions.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            run_project(recipe,temp,registry=registry,base=BASE)
            out=Path(temp)
            self.assertTrue((out/'linguagem_jardim/linguagem_jardim.garden').read_text().startswith('garden '))
            self.assertEqual(len((out/'idioma/idioma.csv').read_text().splitlines()),33)

    def test_failed_recipe_writes_no_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'output'
            recipe={'version':1,'jobs':[{'name':'good','generator':'program','targets':['python']},
                     {'name':'bad','generator':'grammar','params':{'rules':{'start':['<missing>']}},'targets':['text']}]}
            with self.assertRaises(ValueError):run_project(recipe,out,base=BASE)
            self.assertFalse(out.exists())

    def test_extension_cannot_write_outside_output(self):
        reg=default_registry()
        reg.register_target('bad',{'program'},lambda doc,stem:(Artifact('../outside','oops','text/plain'),))
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,'artifact path'):
                run_project({'version':1,'jobs':[{'name':'bad','generator':'program','targets':['bad']}]},Path(temp)/'out',registry=reg)
            self.assertFalse((Path(temp)/'outside').exists())

    def test_duplicate_names_and_invalid_target_domain_are_rejected(self):
        job={'name':'demo','generator':'program','targets':['python']}
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):run_project({'version':1,'jobs':[job,job]},temp)
            with self.assertRaisesRegex(ValueError,'cannot render'):
                run_project({'version':1,'jobs':[{**job,'targets':['svg']}]},temp)

    def test_legacy_cli_and_rng_still_match_original(self):
        import subprocess
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run(['python','-m','markovjunior','--model','Flowers','--size','16','--seed','42','--steps','300','--output',temp],cwd=BASE,check=True,capture_output=True)
            a=Image.open(Path(temp)/'Flowers_42.png').convert('RGBA')
            b=Image.open(BASE/'validation/original/Flowers.png').convert('RGBA')
            self.assertEqual(a.size,b.size)
            self.assertEqual(a.tobytes(),b.tobytes())
        records=json.loads((BASE/'validation/rng_oracle.json').read_text())
        for item in records:
            rng=DotNetRandom(item['seed'])
            self.assertEqual(item['values'],[rng.next() for _ in item['values']])

if __name__=='__main__':unittest.main()
