"""Build the browser bundle from the actual Python package and included assets."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/python-runtime.zip'
OUTPUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted((ROOT / 'markovjunior').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            archive.write(path, path.relative_to(ROOT))
print(OUTPUT, OUTPUT.stat().st_size)
