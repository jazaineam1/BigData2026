"""Poll a documented public score API. Never infer a final from its kickoff time.
The published artifact is a small derived summary for the 20 tracked fixtures,
not a mirror or bulk redistribution of the provider's match database.
"""
import datetime as dt
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'data'/'colombia-2026-ii.json'
TARGET=ROOT/'live.json'
PROVIDER='https://sportscore.com/api/v1/fixtures/'
ALIASES={
'america de cali':'AME','atletico nacional medellin':'NAL','atletico nacional':'NAL',
'deportivo cali':'CAL','millonarios':'MIL','atletico bucaramanga':'BUC',
'independiente santa fe':'SFE','santa fe':'SFE','dep independiente medellin':'DIM','independiente medellin':'DIM',
'aguilas doradas':'AGU','deportiva once caldas':'ONC','once caldas':'ONC','deportes tolima':'TOL',
'cucuta deportivo':'CUC','internacional de bogota':'INT','llaneros fc':'LLA','llaneros':'LLA',
'alianza futbol club':'ALI','alianza fc':'ALI','deportivo pereira':'PER',
'atletico junior barranquilla':'JUN','boyaca chico':'CHI','deportivo pasto':'PAS',
'jaguares de cordoba':'JAG','fortaleza f c':'FOR','fortaleza fc':'FOR'}


def norm(s):
    s=unicodedata.normalize('NFD',str(s or ''))
    return re.sub(r'[^a-z0-9]+',' ',''.join(c for c in s if not unicodedata.combining(c)).lower()).strip()

def valid_date(f,date):
    if not isinstance(date,str):return False
    try: d=dt.date.fromisoformat(date)
    except ValueError:return False
    if f.get('date'):
        return abs((d-dt.date.fromisoformat(f['date'])).days)<=2
    return dt.date(2026,11,10)<=d<=dt.date(2026,11,20)

def identify(base,m,date):
    h,a=ALIASES.get(norm(m.get('home'))),ALIASES.get(norm(m.get('away')))
    if not h or not a:return None
    matches=[f for f in base['fixtures'] if f['home']==h and f['away']==a and valid_date(f,date)]
    return matches[0]['id'] if len(matches)==1 else None

def normalize(base,payload,date):
    if not isinstance(payload,dict) or not isinstance(payload.get('matches'),list):raise ValueError('Invalid feed format')
    out={}
    for m in payload['matches']:
        fid=identify(base,m,date)
        if not fid:continue
        st=str(m.get('status') or '').lower()
        if st not in ('live','finished','upcoming','in_progress','final','completed'):continue
        h,a=m.get('home_score'),m.get('away_score')
        try:score=[int(h),int(a)] if h is not None and a is not None else None
        except (ValueError,TypeError):score=None
        if score is not None and not all(0<=x<=20 for x in score):score=None
        if st in ('finished','final','completed','live','in_progress') and score is None:continue
        status='finished' if st in ('finished','final','completed') else ('live' if st in ('live','in_progress') else 'upcoming')
        new={'id':fid,'status':status,'score':score,'utcDate':date}
        if status=='live':
            minute_match=re.search(r'(?<![0-9])([0-9]{1,3})\s*[\x27\u2019]',str(m.get('status_text') or ''))
            if minute_match:new['minute']=min(90,int(minute_match.group(1)))
        if fid in out and out[fid]!=new:raise ValueError(f'Conflicting data for {fid}')
        out[fid]=new
    return out

def fetch_day(date):
    query=urllib.parse.urlencode({'sport':'football','date':date,'competition':'categoria-primera-a','limit':200})
    req=urllib.request.Request(PROVIDER+'?'+query,headers={'User-Agent':'MatchLab/4.1 (+https://github.com/jazaineam1/BigData2026)'})
    with urllib.request.urlopen(req,timeout=18) as resp:return json.load(resp)

def planned_dates(base,now):
    keys={dt.date(2026,11,4),dt.date(2026,11,5)}
    for offset in range(-1,2):keys.add(now+dt.timedelta(days=offset))
    for f in base['fixtures']:
        date=f.get('date')
        if date:
            v=dt.date.fromisoformat(date)
            if abs((v-now).days)<=2:keys.add(v)
    return sorted(keys)

def main():
    base=json.loads(BASE.read_text())
    now=dt.datetime.now(dt.timezone.utc)
    days=planned_dates(base,now.date())
    observations={};raw_sentinels={};successes=0;failures=[]
    for day in days:
        date=day.isoformat()
        try:payload=fetch_day(date)
        except Exception as e:
            failures.append(f'{date}: {type(e).__name__}')
            continue
        successes+=1
        partial=normalize(base,payload,date)
        for id,item in partial.items():
            if id in observations and observations[id]!=item:raise ValueError(f'Conflicting fixture id: {id}')
            observations[id]=item
        for m in payload.get('matches',[]):
            key=(ALIASES.get(norm(m.get('home'))),ALIASES.get(norm(m.get('away'))))
            if key in [('CUC','SFE'),('MIL','AME')]:raw_sentinels[key]=str(m.get('status') or '').lower()
    if successes==0:raise SystemExit('All provider requests failed; keeping old snapshot.')
    stale=any(s not in ('finished','final','completed') for s in raw_sentinels.values())
    relevant=sorted(observations.values(),key=lambda x:x['id'])
    summary={'provider':'SportScore','competition':'categoria-primera-a','baseVersion':base['meta']['version'],
             'staleReference':stale,'matches':relevant,
             'note':'La fuente puede atrasarse. Solo resultados con estado terminado; no es autoridad oficial.',
             'source':'https://sportscore.com/'}
    prev=json.loads(TARGET.read_text()) if TARGET.exists() else None
    comparison=lambda x:{k:v for k,v in x.items() if k!='updatedAt'}
    if prev is None or comparison(prev)!=summary:
        summary['updatedAt']=now.isoformat()
        temp=TARGET.with_suffix('.json.tmp')
        temp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        temp.replace(TARGET)
        print('CHANGED',len(relevant),'fixtures','finished',sum(x['status']=='finished' for x in relevant),'live',sum(x['status']=='live' for x in relevant),'staleReference',stale,'days',len(days))
    else:print('UNCHANGED',len(relevant),'fixtures','staleReference',stale,'days',len(days))
    if failures:print('Partial fetch failures:',', '.join(failures))

if __name__=='__main__':main()