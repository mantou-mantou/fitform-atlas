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
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT.parent))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    port=server.server_address[1]
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        for name in ['index.html','exercise.html','css/style.css','js/common.js','js/app.js','js/exercise.js','data/exercises.json','assets/illustrations/goblet-squat.svg']:
            with urlopen(f'http://127.0.0.1:{port}/fitform-atlas/{name}',timeout=8) as response:
                assert response.status==200 and len(response.read())>0,name
        print('PASS HTTP: 8 core files reachable under /fitform-atlas/ project subdirectory')
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
        assert page.locator('.exercise-card').count()==4
        assert '4 / 4' in page.locator('#result-count').inner_text()
        page.screenshot(path=str(ROOT.parent/'fitform-atlas_preview_desktop.png'),full_page=True)
        print('PASS Desktop homepage: 4 visible exercise cards')
        page.locator('#exercise-search').fill('bench')
        assert page.locator('.exercise-card').count()==1
        assert page.locator('.exercise-card h3').inner_text()=='槓鈴臥推'
        page.locator('#exercise-search').fill('沒有這個動作')
        assert page.locator('.exercise-card').count()==0
        assert page.locator('#empty-state').is_visible()
        page.locator('#reset-filters').click()
        assert page.locator('.exercise-card').count()==4
        print('PASS Search: english term, empty state, reset')
        page.locator('button[data-category="back"]').click()
        assert page.locator('.exercise-card').count()==1
        assert page.locator('.exercise-card h3').inner_text()=='滑輪下拉'
        assert page.locator('.exercise-card a').get_attribute('href')=='./exercise.html?id=lat-pulldown'
        print('PASS Category filter: back yields lat pulldown and correct detail link')
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
            render(page,'exercise.html','goblet-squat')
            assert page.locator('#detail-name').inner_text()=='高腳杯深蹲'
            dims=page.evaluate('({viewport:innerWidth,scroll:document.documentElement.scrollWidth})')
            assert dims['scroll']<=dims['viewport'],f'detail overflow {width}: {dims}'
            if width==390:page.screenshot(path=str(ROOT.parent/'fitform-atlas_preview_mobile.png'),full_page=True)
            print(f'PASS RWD: {width}px homepage and detail no horizontal overflow')
        # Extension simulation: data-only addition should render a fifth card.
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
        assert page.locator('.exercise-card').count()==5
        page.locator('#exercise-search').fill('擴充驗證用動作')
        assert page.locator('.exercise-card').count()==1
        assert page.locator('.exercise-card a').get_attribute('href')=='./exercise.html?id=extension-fixture'
        render(page,'exercise.html','extension-fixture',library=expanded)
        assert page.locator('#detail-name').inner_text()=='擴充驗證用動作'
        print('PASS Extension simulation: 4→5 data-only fixture, validates, searches and uses shared detail template')
        assert errors==[],f'Browser JS exceptions: {errors}' 
        print('PASS Browser: no uncaught JS errors')
        browser.close()


if __name__=='__main__':main()
