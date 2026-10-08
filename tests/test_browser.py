import json
import unittest
from markovjunior.procedural.browser import browser_generate


class BrowserTests(unittest.TestCase):
    def test_browser_returns_seeded_geometry_and_real_backends(self):
        recipe = {'version': 1, 'seed': 42, 'jobs': [
            {'name': 'garden', 'generator': 'scene3d', 'params': {'trees': 2, 'depth': 2}, 'targets': ['scene3d-json']},
            {'name': 'code', 'generator': 'program', 'targets': ['python', 'c', 'cpp', 'rust']},
        ]}
        first = json.loads(browser_generate(recipe))
        self.assertEqual(first, json.loads(browser_generate(recipe)))
        self.assertEqual(len(first['scenes'][0]['objects']), 22)
        self.assertEqual(len(first['files']), 5)
        source = next(f['content'] for f in first['files'] if f['name'].endswith('.py'))
        namespace = {}
        exec(source, namespace)
        self.assertIsInstance(namespace['proc_000'](12, -4), int)
        recipe['seed'] = 43
        self.assertNotEqual(first['scenes'], json.loads(browser_generate(recipe))['scenes'])

    def test_scene3d_budget_is_checked(self):
        with self.assertRaises(ValueError):
            browser_generate({'version': 1, 'jobs': [{'name': 'garden', 'generator': 'scene3d',
                'params': {'depth': 6}, 'targets': ['scene3d-json']}]})
