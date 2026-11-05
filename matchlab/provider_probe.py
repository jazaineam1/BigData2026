import json, urllib.request, urllib.parse, datetime
base="https://sportscore.com/api/v1/"
for endpoint,args in [
    ("search/",{"q":"Categoria Primera A","sport":"football","limit":20}),
    ("fixtures/",{"sport":"football","date":"2026-11-04","limit":200}),
    ("fixtures/",{"sport":"football","date":"2026-11-06","limit":200}),
    ("standings/",{"sport":"football","slug":"categoria-primera-a"}),
]:
    url=base+endpoint+"?"+urllib.parse.urlencode(args)
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"MatchLab/4.1 (+https://github.com/jazaineam1/BigData2026)"})
        with urllib.request.urlopen(req,timeout=20) as r:
            x=json.load(r)
        print(endpoint, args.get("date"),"kind",type(x).__name__,"keys",list(x.keys()) if isinstance(x,dict) else "list","count",len(x) if isinstance(x,list) else "dict")
        raw=json.dumps(x,ensure_ascii=False)
        print("sample",raw[:2300])
    except Exception as exc:
        print(endpoint,args.get("date"),"ERROR",repr(exc))
