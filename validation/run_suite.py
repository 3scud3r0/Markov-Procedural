"""Reproduce the original and Python cases with per-case time limits."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--language',choices=['original','python','both'],default='both')
    p.add_argument('--dotnet',default='dotnet')
    p.add_argument('--case',help='Run one case ID')
    args=p.parse_args()
    base=Path(__file__).resolve().parents[1]
    validation=base/'validation'
    cases=json.loads((validation/'cases.json').read_text())
    cases=[c for c in cases if args.case is None or c['id']==args.case]
    for lang in (['original','python'] if args.language=='both' else [args.language]):
        output=validation/lang
        output.mkdir(exist_ok=True)
        for c in cases:
            for ext in ('.state','.json','.png','.vox','.error','.timeout'):
                (output/(c['id']+ext)).unlink(missing_ok=True)
            timeout=35 if c['model'] in ('MultiSokoban8','SokobanLevel2') else 240
            with tempfile.TemporaryDirectory() as temp:
                manifest=Path(temp)/'case.json'
                manifest.write_text(json.dumps([c]))
                command=[args.dotnet,str(validation/'reference/bin/Reference.dll'),str(base/'original'),str(manifest),str(output)] if lang=='original' else [sys.executable,str(validation/'run_python.py'),str(manifest),str(base),str(output)]
                with (output/(c['id']+'.log')).open('w') as log:
                    try:
                        result=subprocess.run(command,stdout=log,stderr=log,timeout=timeout)
                        print(lang,c['id'],result.returncode,flush=True)
                    except subprocess.TimeoutExpired:
                        (output/(c['id']+'.timeout')).write_text(f'Execution exceeded {timeout} seconds')
                        print(lang,c['id'],'TIMEOUT',flush=True)

if __name__=='__main__':
    main()
