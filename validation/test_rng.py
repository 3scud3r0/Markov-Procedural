"""Regression against 14,208 actual System.Random outputs from .NET 10."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from markovjunior import DotNetRandom

class RandomCompatibility(unittest.TestCase):
    def test_original_dotnet_vectors(self):
        vectors=json.loads(Path(__file__).with_name('rng_oracle.json').read_text())
        for record in vectors:
            with self.subTest(seed=record['seed']):
                random=DotNetRandom(record['seed'])
                self.assertEqual(record['values'],[random.next() for _ in record['values']])

if __name__=='__main__':
    unittest.main()
