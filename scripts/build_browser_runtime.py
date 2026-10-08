"""Build the browser bundle from the actual Python package and included assets."""
from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/python-runtime.zip'
OUTPUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    archive.write(ROOT / 'procedural.py', 'procedural.py')
    for path in sorted((ROOT / 'markovjunior').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            archive.write(path, path.relative_to(ROOT))
print(OUTPUT, OUTPUT.stat().st_size)
catalog = json.loads((ROOT / 'examples/language/catalog.json').read_text())
for entry in catalog:
    folder = ROOT / 'examples/language' / entry['id']
    entry['files'] = [{'name': p.relative_to(folder).as_posix(), 'content': p.read_text()}
                      for p in sorted(folder.glob('*.mp'))]
(ROOT / 'docs/examples.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
