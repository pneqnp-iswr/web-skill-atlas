#!/usr/bin/env python3
from pathlib import Path
from difflib import SequenceMatcher
import json,re
ROOT=Path(__file__).resolve().parents[1]
skills=json.loads((ROOT/'data/skills.json').read_text())
def norm(s): return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
hits=[]
for i,a in enumerate(skills):
 for b in skills[i+1:]:
  score=SequenceMatcher(None,norm(a['name']),norm(b['name'])).ratio()
  ad=(a.get('source_detail') or '').strip(); bd=(b.get('source_detail') or '').strip()
  same_locator=(a.get('source_url')==b.get('source_url') and bool(ad) and ad==bd)
  if same_locator or score>=0.92: hits.append((score,a['slug'],b['slug'],same_locator))
for h in sorted(hits,reverse=True): print(f'{h[0]:.2f}\t{h[1]}\t{h[2]}'+('\tSAME_SOURCE' if h[3] else ''))
print(f'Candidates: {len(hits)}')
