"""Compare actual independently generated states, metadata, RGBA pixels and VOX bytes."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np


def compare(base):
    root=base/'validation'
    cases=json.loads((root/'cases.json').read_text())
    records=[]
    for c in cases:
        id=c['id']
        a,b=root/'original'/id,root/'python'/id
        record=dict(case=c)
        if not a.with_suffix('.state').exists() or not b.with_suffix('.state').exists():
            record['status']='missing'
            record['errors']={lang: next(((root/lang/(id+ext)).read_text() for ext in ('.error','.timeout') if (root/lang/(id+ext)).exists()),'pending') for lang in ('original','python')}
        else:
            aa,bb=a.with_suffix('.state').read_bytes(),b.with_suffix('.state').read_bytes()
            record['state_equal']=aa==bb
            record['state_sha256_original']=hashlib.sha256(aa).hexdigest()
            record['state_sha256_python']=hashlib.sha256(bb).hexdigest()
            ma,mb=json.loads(a.with_suffix('.json').read_text()),json.loads(b.with_suffix('.json').read_text())
            record['metadata_equal']=ma==mb
            record['original_metadata']=ma
            record['python_metadata']=mb
            if a.with_suffix('.png').exists() and b.with_suffix('.png').exists():
                ai,bi=np.array(Image.open(a.with_suffix('.png')).convert('RGBA')),np.array(Image.open(b.with_suffix('.png')).convert('RGBA'))
                equal=ai.shape==bi.shape and np.array_equal(ai,bi)
                record['pixels_equal']=equal
                record['different_pixels']=int(np.any(ai!=bi,axis=2).sum()) if ai.shape==bi.shape else None
                record['pixel_sha256_original']=hashlib.sha256(ai.tobytes()).hexdigest()
                record['pixel_sha256_python']=hashlib.sha256(bi.tobytes()).hexdigest()
            if a.with_suffix('.vox').exists() and b.with_suffix('.vox').exists():
                record['vox_equal']=a.with_suffix('.vox').read_bytes()==b.with_suffix('.vox').read_bytes()
            record['status']='pass' if all(record.get(k,True) for k in ('state_equal','metadata_equal','pixels_equal','vox_equal')) else 'fail'
        records.append(record)
    summary={k:sum(r['status']==k for r in records) for k in ('pass','fail','missing')}
    (root/'report.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2))
    print(summary)
    for r in records:
        if r['status']=='fail':
            print(r['case']['id'],{k:r[k] for k in ('state_equal','metadata_equal','pixels_equal','vox_equal','different_pixels') if k in r})
    return records

if __name__=='__main__':
    compare(Path(__file__).resolve().parents[1])
