"""Browser regression tests for full-table and feed-integration invariants."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
site = (root / 'MatchLab_4_1_en_vivo.html').read_text()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    issues=[]
    page.on('pageerror', lambda err: issues.append(str(err)))
    # Network responses are fixed to isolate the simulation and test the provider edge cases.
    page.route('https://sportscore.com/**', lambda route: route.fulfill(status=200, content_type='application/json', body=json.dumps({'matches': []})))
    page.route('**/live.json*', lambda route: route.fulfill(status=200, content_type='application/json', body=json.dumps({'baseVersion':'4.0.0','updatedAt':None,'staleReference': True,'matches': []})))
    page.set_content(site, wait_until='load')
    page.wait_for_timeout(600)
    assert not issues, issues
    assert page.locator('#table-body tr').count() == 20
    assert set(page.locator('#table-body tr td:nth-child(3)').all_inner_texts()) == {'19'}
    assert page.evaluate('MatchLabTest.getData().fixtures.length') == 20
    assert page.locator('#total-universe').inner_text() == '3.486.784.401'
    # Conditional fixture update: never count a fixture twice.
    result = page.evaluate('''() => {
      const f=MatchLabTest.getData().fixtures.find(x=>x.id==='18-FOR-DIM');
      const rows=[{home:f.home,away:f.away,status:'finished',score:[2,1],dateUTC:'2026-11-07',minute:null}];
      return MatchLabTest.newStateFromFeed(MatchLabTest.getData(),rows);
    }''')
    assert len(result['done'])==1
    assert len(result['data']['fixtures'])==19
    fort = next(x for x in result['data']['teams'] if x['id']=='FOR')
    med = next(x for x in result['data']['teams'] if x['id']=='DIM')
    assert fort['pj']==18 and med['pj']==18
    assert fort['pts']==fort['w']*3+fort['d']
    assert med['pts']==med['w']*3+med['d']
    # A live/in-progress score MUST NOT be counted as final.
    x=page.evaluate('''() => MatchLabTest.newStateFromFeed(MatchLabTest.getData(),[
      {home:'FOR',away:'DIM',status:'live',score:[1,0],dateUTC:'2026-11-07',minute:60}
    ])''')
    assert len(x['done'])==0 and len(x['live'])==1 and len(x['data']['fixtures'])==20
    # Update app, and verify both projection and real table.
    page.evaluate('''d => MatchLabTest.feedCommit(d, [])''', result['data'])
    assert page.evaluate('MatchLabTest.getData().fixtures.length')==19
    assert set(page.locator('#table-body tr td:nth-child(3)').all_inner_texts())=={'19'}
    page.locator('[data-table-mode="base"]').click()
    assert set(page.locator('#table-body tr td:nth-child(3)').all_inner_texts())=={'17','18'}
    page.locator('[data-table-mode="expected"]').click()
    assert set(page.locator('#table-body tr td:nth-child(3)').all_inner_texts())=={'19'}
    # Paths with 19 fixtures, 3^19; no phantom 38 fixtures.
    assert page.locator('#total-universe').inner_text()=='1.162.261.467'
    assert not issues, issues
    browser.close()
print('Browser regression: PASS')