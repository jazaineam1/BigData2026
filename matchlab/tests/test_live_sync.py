import sys, pathlib, json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from live_sync import norm,normalize,valid_date,planned_dates
base=json.loads((pathlib.Path(__file__).resolve().parents[1]/'data'/'colombia-2026-ii.json').read_text())
assert norm('Águilas Doradas')=='aguilas doradas'
assert valid_date(base['fixtures'][0],'2026-11-06')
assert not valid_date(base['fixtures'][0],'2025-11-06')
valid={'matches':[{'home':'Fortaleza F.C','away':'Dep.Independiente Medellin','home_score':'2','away_score':'1','status':'finished'}]}
row=normalize(base,valid,'2026-11-07')
assert row['18-FOR-DIM']['status']=='finished' and row['18-FOR-DIM']['score']==[2,1]
assert not normalize(base,{'matches':[{'home':'Fortaleza F.C','away':'Dep.Independiente Medellin','home_score':None,'away_score':None,'status':'finished'}]},'2026-11-07')
assert not normalize(base,{'matches':[{'home':'Fortaleza F.C','away':'Dep.Independiente Medellin','home_score':'2','away_score':'1','status':'finished'}]},'2023-11-07')
print('live_sync: PASS')