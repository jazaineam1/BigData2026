import json, urllib.request, urllib.parse
base='https://sportscore.com/api/widget/'
for endpoint,kwargs in [('standings/',{'sport':'football','slug':'categoria-primera-a'}),('topscorers/',{'sport':'football','slug':'categoria-primera-a','limit':'20','stat':'goals'}),('topscorers/',{'sport':'football','slug':'categoria-primera-a','limit':'20','stat':'assists'}),('team/',{'sport':'football','slug':'dep-independiente-medellin','limit':'5'})]:
 url=base+endpoint+'?'+urllib.parse.urlencode(kwargs)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MatchLab/4.2'}),timeout=15) as r: j=json.load(r)
  print(endpoint,kwargs.get('stat',''), 'keys',list(j)[:15], 'total chars',len(json.dumps(j)))
  if endpoint=='standings/':
   tables=j.get('tables',[]);rows=[x for t in tables for x in t.get('rows',[])]
   print('TABLES',len(tables),'ROWS',len(rows));print('TEAMS',json.dumps([{k:r.get(k) for k in ('team','team_slug','team_logo','p','pts')} for r in rows],ensure_ascii=False))
  else: print('BODY',json.dumps(j,ensure_ascii=False)[:6000])
 except Exception as e:print(endpoint,'ERROR',repr(e))
