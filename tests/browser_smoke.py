"""Chromium DOM-injection smoke test (works in restricted browser sandboxes).

The sandbox may block browser network navigation; this tests actual HTML/CSS/JS with
fetch mocked from the project's JSON. HTTP delivery is checked separately using urllib.
Not equivalent to a live GitHub Pages test.
"""
import base64
import copy
import tempfile
import shutil
import functools
import http.server
import json
import re
import threading
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/exercises.json').read_text(encoding='utf-8'))
ROW=next(exercise for exercise in DATA['exercises'] if exercise['id']=='one-arm-dumbbell-row')
TOTAL=len(DATA['exercises'])
CSS=(ROOT/'css/style.css').read_text(encoding='utf-8')
IMAGES={str(path.relative_to(ROOT)): 'data:image/svg+xml;base64,'+base64.b64encode(path.read_bytes()).decode('ascii') for path in (ROOT/'assets/illustrations').glob('*.svg')}


def render(page, filename, id=None, library=None):
    html=(ROOT/filename).read_text(encoding='utf-8')
    # Strip network resource tags; load same bytes via browser-injected assets.
    html=re.sub(r'<script\b[^>]+src="[^"]+"[^>]*></script>','',html)
    html=re.sub(r'<link\b[^>]+(?:stylesheet|icon)[^>]*>','',html)
    page.goto('about:blank')
    page.set_content(html,wait_until='domcontentloaded')
    page.add_style_tag(content=CSS)
    if id:
        page.evaluate('(id)=>history.pushState({}, "", "about:blank?id="+encodeURIComponent(id))',id)
    page.evaluate('(data)=>{window.fetch=async()=>({ok:true,json:async()=>data});}',library or DATA)
    page.add_script_tag(content=(ROOT/'js/common.js').read_text(encoding='utf-8'))
    page.add_script_tag(content=(ROOT/('js/app.js' if filename=='index.html' else 'js/exercise.js')).read_text(encoding='utf-8'))
    page.wait_for_timeout(150)
    page.evaluate('(images)=>{document.querySelectorAll("img").forEach(img=>{const found=Object.entries(images).find(([path])=>img.getAttribute("src")?.endsWith(path));if(found)img.src=found[1]})}',IMAGES)


def check_http_assets():
    for directory,prefix in ((ROOT,''),(ROOT.parent,'fitform-atlas/')):
        handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(directory))
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        port=server.server_address[1]
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            for name in ['index.html','exercise.html?id=one-arm-dumbbell-row','css/style.css','js/common.js','js/app.js','js/exercise.js','data/exercises.json',ROW['illustration']]:
                with urlopen(f'http://127.0.0.1:{port}/{prefix}{name}',timeout=8) as response:
                    assert response.status==200 and len(response.read())>0,name
            print(f'PASS HTTP: 8 core files including row SVG reachable under /{prefix}')
        finally:
            server.shutdown();server.server_close()


def main():
    check_http_assets()
    errors=[]
    with sync_playwright() as p:
        try:
            browser=p.chromium.launch(headless=True)
        except Exception:
            fallback=Path('/usr/bin/chromium')
            if not fallback.is_file():raise
            browser=p.chromium.launch(headless=True,executable_path=str(fallback),args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        render(page,'index.html')
        assert page.locator('.exercise-card').count()==TOTAL
        assert f'{TOTAL} / {TOTAL}' in page.locator('#result-count').inner_text()
        page.screenshot(path=str(ROOT.parent/'fitform-atlas_preview_desktop.png'),full_page=True)
        print(f'PASS Desktop homepage: {TOTAL} visible exercise cards')
        page.locator('#exercise-search').fill('bench')
        assert page.locator('.exercise-card').count()==1
        assert page.locator('.exercise-card h3').inner_text()=='槓鈴臥推'
        page.locator('#exercise-search').fill('沒有這個動作')
        assert page.locator('.exercise-card').count()==0
        assert page.locator('#empty-state').is_visible()
        page.locator('#reset-filters').click()
        assert page.locator('.exercise-card').count()==TOTAL
        print('PASS Search: english term, empty state, reset')
        page.locator('button[data-category="back"]').click()
        back=[exercise for exercise in DATA['exercises'] if exercise['category']=='back']
        assert page.locator('.exercise-card').count()==len(back)
        assert page.locator('.exercise-card h3').all_inner_texts()==[exercise['name'] for exercise in back]
        assert page.locator('a[href="./exercise.html?id=one-arm-dumbbell-row"]').count()==1
        print('PASS Category filter: back includes lat pulldown and one-arm dumbbell row')
        for query in ('單臂啞鈴划船','單手划船','one-arm dumbbell row','single arm row','ROW'):
            page.locator('#exercise-search').fill(query)
            assert page.locator('.exercise-card').count()==1,query
            assert page.locator('.exercise-card h3').inner_text()==ROW['name']
        page.locator('#exercise-search').fill('划船')
        page.locator('button[data-category="chest"]').click()
        assert page.locator('#empty-state').is_visible()
        page.locator('#reset-filters').click()
        assert page.locator('.exercise-card').count()==TOTAL
        print('PASS Row search: Chinese, aliases, English case, combined filters and reset')
        render(page,'exercise.html',ROW['id'])
        assert page.locator('#detail-name').inner_text()==ROW['name']
        assert page.locator('#detail-en').inner_text()==ROW['nameEn']
        assert page.locator('#detail-steps li').count()==len(ROW['steps'])
        assert page.locator('#detail-mistakes .mistake-card').count()==len(ROW['mistakes'])
        assert page.locator('#detail-safety li').count()==len(ROW['safetyTips'])
        assert page.locator('#detail-primary .info-tag').all_inner_texts()==ROW['muscles']['primary']
        assert page.locator('#detail-secondary .info-tag').all_inner_texts()==ROW['muscles']['secondary']
        assert page.locator('#detail-equipment .info-tag').all_inner_texts()==ROW['equipment']
        assert page.locator('#detail-image').get_attribute('alt')
        page.wait_for_function('document.querySelector("#detail-image").complete && document.querySelector("#detail-image").naturalWidth>0')
        links=page.locator('#detail-sources a')
        assert links.count()==len(ROW['sources'])
        for index,source in enumerate(ROW['sources']):
            assert links.nth(index).get_attribute('href')==source['url']
            assert links.nth(index).get_attribute('target')=='_blank'
            assert set(links.nth(index).get_attribute('rel').split())=={'noopener','noreferrer'}
        assert page.locator('.breadcrumbs a').nth(1).get_attribute('href')=='./index.html#library'
        assert page.locator('#related-grid .exercise-card h3').first.inner_text()=='滑輪下拉'
        print('PASS Row detail: all lists, SVG, safe source links, return link and related back exercise')
        for exercise in DATA['exercises']:
            render(page,'exercise.html',exercise['id'])
            assert page.locator('#detail-name').inner_text()==exercise['name']
            assert page.locator('#detail-content').is_visible()
        print('PASS Regression: all existing and new ids render in the shared detail template')
        render(page,'exercise.html','lat-pulldown')
        assert page.locator('#detail-name').inner_text()=='滑輪下拉'
        assert page.locator('#detail-steps li').count()==3
        assert page.locator('#detail-mistakes .mistake-card').count()==2
        assert page.locator('#detail-sources a').count()==2
        print('PASS Detail: title, 3 instructions, 2 mistakes, 2 source links')
        render(page,'exercise.html','nonexistent')
        assert page.locator('#detail-error').is_visible()
        assert '找不到' in page.locator('#detail-error-title').inner_text()
        print('PASS Unknown id: friendly fallback')
        for width in (320,390,768,1440):
            page.set_viewport_size({'width':width,'height':900})
            render(page,'index.html')
            dims=page.evaluate('({viewport:innerWidth,scroll:document.documentElement.scrollWidth})')
            assert dims['scroll']<=dims['viewport'],f'home overflow {width}: {dims}'
            if width==390:page.screenshot(path=str(ROOT.parent/'fitform-atlas_preview_mobile_home.png'),full_page=True)
            render(page,'exercise.html',ROW['id'])
            assert page.locator('#detail-name').inner_text()==ROW['name']
            dims=page.evaluate('({viewport:innerWidth,scroll:document.documentElement.scrollWidth})')
            assert dims['scroll']<=dims['viewport'],f'detail overflow {width}: {dims}'
            if width==390:page.screenshot(path=str(ROOT.parent/'fitform-atlas_preview_mobile.png'),full_page=True)
            print(f'PASS RWD: {width}px homepage and detail no horizontal overflow')
        # Extension simulation: data-only addition should render one more card.
        # This fixture does NOT mean a real new-chat AI task has been tested.
        import sys
        sys.path.insert(0,str(ROOT/'tests'))
        from validate_content import validate
        expanded=copy.deepcopy(DATA)
        extra=copy.deepcopy(expanded['exercises'][0])
        extra['id']='extension-fixture'
        extra['name']='擴充驗證用動作'
        extra['nameEn']='EXTENSION FIXTURE'
        extra['category']='back'
        extra['illustration']='assets/illustrations/extension-fixture.svg'
        expanded['exercises'].append(extra)
        with tempfile.TemporaryDirectory() as tmp:
            new_root=Path(tmp)
            (new_root/'assets/illustrations').mkdir(parents=True)
            shutil.copyfile(ROOT/'assets/illustrations/bench-press.svg', new_root/'assets/illustrations/extension-fixture.svg')
            for exercise in DATA['exercises']:
                shutil.copyfile(ROOT/exercise['illustration'], new_root/exercise['illustration'])
            assert validate(expanded,new_root)==[]
        render(page,'index.html',library=expanded)
        assert page.locator('.exercise-card').count()==TOTAL+1
        page.locator('#exercise-search').fill('擴充驗證用動作')
        assert page.locator('.exercise-card').count()==1
        assert page.locator('.exercise-card a').get_attribute('href')=='./exercise.html?id=extension-fixture'
        render(page,'exercise.html','extension-fixture',library=expanded)
        assert page.locator('#detail-name').inner_text()=='擴充驗證用動作'
        print(f'PASS Extension simulation: {TOTAL}→{TOTAL+1} data-only fixture, validates, searches and uses shared detail template')
        assert errors==[],f'Browser JS exceptions: {errors}' 
        print('PASS Browser: no uncaught JS errors')
        browser.close()


if __name__=='__main__':main()
