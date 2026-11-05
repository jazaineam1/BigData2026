from pathlib import Path
from playwright.sync_api import sync_playwright
import json

PATH=Path(__file__).resolve().parents[1]/'MatchLab_4_1_en_vivo.html'
with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for viewport in [{'width':1440,'height':900},{'width':390,'height':844}]:
    page=browser.new_page(viewport=viewport)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('https://sportscore.com/**',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({'sport':'football','date':'2026-11-05','count':0,'matches':[]})))
    page.set_content(PATH.read_text(),wait_until='load');page.wait_for_timeout(800)
    print('viewport',viewport,'errors',errors, 'table',page.locator('#table-status').inner_text()[:130])
    print('rows',page.locator('#table-body tr').count(), 'pj',page.locator('#table-body tr').first.locator('td').nth(2).inner_text())
    print('sim',page.locator('#sim-status').inner_text(),'avg',page.locator('#expected-points').inner_text())
    assert not errors
    assert page.locator('#table-body tr').count()==20
    assert page.locator('#table-body tr').first.locator('td').nth(2).inner_text()=='19'
    page.locator('[data-table-mode="base"]').click()
    assert page.locator('#table-body tr').first.locator('td').nth(2).inner_text()=='17'
    page.locator('[data-table-mode="expected"]').click()
    print('expected-pj',page.locator('#table-body tr').first.locator('td').nth(2).inner_text())
    assert page.locator('#table-body tr').first.locator('td').nth(2).inner_text()=='19'
    page.screenshot(path=f'/mnt/data/matchlab5/qa_{viewport["width"]}.png',full_page=False)
    print('scrollWidth',page.evaluate('document.documentElement.scrollWidth'),'innerWidth',viewport['width'])
    page.close()
  browser.close()