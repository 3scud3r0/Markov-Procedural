"""Package sources, browser, reference, evidence, wheel and readable source TXT."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'downloads'
OUTPUT.mkdir(exist_ok=True)
tracked = subprocess.check_output(
    ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT
).decode().split('\0')
paths = sorted({name for name in tracked if name and not name.startswith('downloads/')
                and name not in ('manifesto_entrega.json', 'codigo_markov_1_0.txt')
                and (ROOT / name).is_file()})
extensions = {'.py', '.mp', '.cs', '.xml', '.csproj', '.sh', '.toml', '.json',
              '.c', '.cpp', '.h', '.rs', '.go', '.mjs', '.js', '.cjs', '.ts',
              '.lua', '.sql', '.garden', '.svg', '.html', '.css', '.yml', '.md'}
text_path = OUTPUT / 'codigo_markov_1_0.txt'
with text_path.open('w', encoding='utf-8') as output:
    output.write('MARKOV 1.0 — PROCEDURAL STUDIO\nReadable source, configuration, examples and documentation.\nCompiled Python 3.12 bytecode is included separately, together with the wheel.\n\n')
    for name in paths:
        path = ROOT / name
        if path.suffix not in extensions and not path.name.startswith('requirements'):
            continue
        output.write('\n' + '=' * 80 + '\nFILE: ' + name + '\n' + '=' * 80 + '\n')
        output.write(path.read_text(encoding='utf-8-sig') + '\n')
release = {'schema': 'markov.release/1', 'version': '1.0.0',
           'validation': json.loads((ROOT / 'validation/studio_report.json').read_text()),
           'files': []}
for name in paths:
    content = (ROOT / name).read_bytes()
    release['files'].append({'path': name, 'bytes': len(content),
                             'sha256': hashlib.sha256(content).hexdigest()})
content = text_path.read_bytes()
release['files'].append({'path': text_path.name, 'bytes': len(content),
                         'sha256': hashlib.sha256(content).hexdigest()})
archive_path = OUTPUT / 'Markov_Studio_1.0.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name in paths:
        archive.write(ROOT / name, 'Markov_Studio_1.0/' + name)
    archive.write(text_path, 'Markov_Studio_1.0/' + text_path.name)
    archive.writestr('Markov_Studio_1.0/manifesto_entrega.json', json.dumps(release, ensure_ascii=False, indent=2))
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
print('ZIP', archive_path.stat().st_size, 'bytes;', len(paths), 'source/evidence files')
print('TXT', text_path.stat().st_size, 'bytes')
