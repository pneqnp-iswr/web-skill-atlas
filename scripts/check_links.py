#!/usr/bin/env python3
import argparse,json,time,urllib.request,urllib.error
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--limit',type=int,default=0);P.add_argument('--retries',type=int,default=2);a=P.parse_args()
root=Path(__file__).resolve().parents[1]; skills=json.loads((root/'data/skills.json').read_text())
urls=sorted({s['source_url'] for s in skills}); urls=urls[:a.limit] if a.limit else urls
hard=[];transient=[];ok=0
for url in urls:
 result=None
 for attempt in range(a.retries+1):
  try:
   req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'web-skill-atlas-link-checker/1.0'})
   with urllib.request.urlopen(req,timeout=15) as r: result=r.status; break
  except urllib.error.HTTPError as e:
   result=e.code
   if e.code in (403,408,425,429,500,502,503,504): time.sleep(1+attempt); continue
   break
  except Exception as e:
   result=str(e); time.sleep(1+attempt)
 if isinstance(result,int) and 200<=result<400: ok+=1
 elif result in (404,410): hard.append((url,result))
 else: transient.append((url,result))
print(f'checked={len(urls)} ok={ok} hard_dead={len(hard)} transient={len(transient)}')
for x in hard: print('HARD',*x)
for x in transient: print('TRANSIENT',*x)
raise SystemExit(1 if hard else 0)
