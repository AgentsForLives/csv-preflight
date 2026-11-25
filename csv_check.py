"""Conservative UTF-8 CSV audit. No guessing or automatic modifications."""
import argparse,csv,json,io
from collections import defaultdict
from pathlib import Path

def audit(text,required=(),key=None):
    reader=csv.reader(io.StringIO(text.lstrip('\ufeff')),strict=True)
    header=next(reader,None)
    if not header:raise ValueError('CSV has no header')
    if any(not name.strip() for name in header):raise ValueError('Empty column name')
    if len(set(header))!=len(header):raise ValueError('Duplicate header names')
    absent=set(required)-set(header)
    if absent:raise ValueError('Missing required columns: '+', '.join(sorted(absent)))
    if key and key not in header:raise ValueError('Key column absent')
    issues=[];seen={};keys=defaultdict(list);count=0
    for line,row in enumerate(reader,2):
        count+=1
        if len(row)!=len(header):
            issues.append({'row':line,'type':'column_count','expected':len(header),'actual':len(row)});continue
        values=dict(zip(header,row));sig=tuple(row)
        if sig in seen:issues.append({'row':line,'type':'exact_duplicate','first_row':seen[sig]})
        else:seen[sig]=line
        for field in required:
            if not values[field].strip():issues.append({'row':line,'type':'required_empty','column':field})
        if key:
            val=values[key]
            if not val.strip():issues.append({'row':line,'type':'key_empty','column':key})
            else:keys[val].append((line,sig))
    for val,items in keys.items():
        if len({sig for _,sig in items})>1:issues.append({'type':'conflicting_key','key':val,'rows':[n for n,_ in items]})
    return {'rows':count,'columns':header,'issues':issues,'modifications':0,'note':'All cells remain strings; source is never modified.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--required',nargs='*',default=[]);p.add_argument('--key');p.add_argument('--output',required=True);a=p.parse_args()
    src=Path(a.input);dest=Path(a.output)
    if src.resolve()==dest.resolve():p.error('Output must differ from input')
    if src.stat().st_size>5*1024*1024:p.error('File exceeds 5 MB')
    result=audit(src.read_text(encoding='utf-8-sig'),a.required,a.key)
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
