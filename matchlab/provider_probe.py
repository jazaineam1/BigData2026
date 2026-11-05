import json,urllib.request,urllib.parse
for date in ['2026-11-04','2026-11-05','2026-11-06','2026-11-07','2026-11-08','2026-11-09','2026-11-12']:
  args=urllib.parse.urlencode({'sport':'football','date':date,'competition':'categoria-primera-a','limit':200})
  req=urllib.request.Request('https://sportscore.com/api/v1/fixtures/?'+args,headers={'User-Agent':'MatchLab/4.1 (+https://github.com/jazaineam1/BigData2026)'})
  try:
    with urllib.request.urlopen(req,timeout=20) as res: data=json.load(res)
    print(date,'count',data.get('count'),'fixtures',[(m.get('home'),m.get('away'),m.get('home_score'),m.get('away_score'),m.get('status'),m.get('time')) for m in data.get('matches',[])[:30]])
  except Exception as exc:print(date,'ERROR',repr(exc))
