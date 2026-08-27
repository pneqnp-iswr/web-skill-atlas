#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'
skills=json.loads((D/'skills.json').read_text()); cats={x['name'] for x in json.loads((D/'categories.json').read_text())}
required={'id','name','slug','description','category','subcategory','type','source_url','source_platform','quality_score','status','last_verified','canonical'}
statuses={'verified','partially-verified','experimental','deprecated','unavailable','duplicate','archived'}
seen=set(); ids=set(); errors=[]
for i,s in enumerate(skills):
 miss=required-set(s)
 if miss: errors.append(f'{i}: missing {sorted(miss)}')
 if s.get('slug') in seen: errors.append(f"duplicate slug: {s.get('slug')}")
 seen.add(s.get('slug'))
 if s.get('id') in ids: errors.append(f"duplicate id: {s.get('id')}")
 ids.add(s.get('id'))
 if s.get('category') not in cats: errors.append(f"{s.get('slug')}: invalid category")
 if s.get('status') not in statuses: errors.append(f"{s.get('slug')}: invalid status")
 q=s.get('quality_score');
 if not isinstance(q,int) or not 0<=q<=100: errors.append(f"{s.get('slug')}: invalid score")
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',s.get('last_verified','')): errors.append(f"{s.get('slug')}: invalid date")
 if not str(s.get('source_url','')).startswith(('https://','http://')): errors.append(f"{s.get('slug')}: invalid source URL")
if errors:
 print('\n'.join(errors)); sys.exit(1)
print(f'OK: {len(skills)} skills, {len(cats)} taxonomy categories, {len(seen)} unique slugs')
