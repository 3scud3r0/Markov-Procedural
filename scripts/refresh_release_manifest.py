"""Refresh file hashes without ever writing to a file being inspected."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / 'manifesto_entrega.json'
manifest = json.loads(MANIFEST_PATH.read_text())
paths = subprocess.check_output(
    ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT
).decode().split('\0')
manifest['files'] = []
for name in sorted(set(paths)):
    if not name or name == MANIFEST_PATH.name:
        continue
    source_path = ROOT / name
    if not source_path.is_file():
        continue
    content = source_path.read_bytes()
    manifest['files'].append({'path': name, 'bytes': len(content),
                              'sha256': hashlib.sha256(content).hexdigest()})
MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('Manifest updated:', len(manifest['files']), 'files')
