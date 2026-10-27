# 수정 화면 미리보기: 칸 200px, 세로 사진 전체 보임(contain) + 흐린 배경
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'tall.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    vid=pg.url.split('/view/')[1].split('?')[0]
    pg.goto(B+'/photo/'+vid); pg.wait_for_function("document.querySelector('.sp-p__thumbbox-media').complete")
    box=pg.locator('.sp-p__thumbbox').bounding_box(); check(abs(box['height']-200)<=1,f'칸 높이 200 ({box["height"]})')
    r=pg.locator('.sp-p__thumbbox-media').evaluate("e=>{const b=e.getBoundingClientRect();return [b.width,b.height,e.naturalWidth/e.naturalHeight,b.width/b.height]}")
    check(abs(r[1]-200)<1 and abs(r[2]-r[3])<0.01,f'세로 사진 전체 보임(높이 200·비율 그대로) {r}')
    bl=pg.locator('.sp-p__thumbbox-blur'); bb=bl.bounding_box(); check(bb['x']<box['x']-30 and bb['y']<box['y']-30,f'흐린 층이 칸보다 큼 {bb}')
    check(bl.count()==1 and bl.get_attribute('aria-hidden')=='true' and 'blur' in bl.evaluate('e=>getComputedStyle(e).filter'),'흐린 배경(화면 읽기 제외)')
    pg.screenshot(path=S+'thumb-tall.png')
    d=b.new_context(viewport={'width':390,'height':844},color_scheme='dark'); d.add_cookies(c.cookies()); dp=d.new_page(); dp.goto(B+'/photo/'+vid); dp.wait_for_timeout(300); dp.screenshot(path=S+'thumb-tall-d.png')
    # 파노라마: 폭에 맞고 위아래 가운데
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'pano.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pid=pg.url.split('/view/')[1].split('?')[0]
    pg.goto(B+'/photo/'+pid); pg.wait_for_function("document.querySelector('.sp-p__thumbbox-media').complete")
    m=pg.locator('.sp-p__thumbbox-media').bounding_box(); bx=pg.locator('.sp-p__thumbbox').bounding_box()
    check(abs(m['width']-bx['width'])<1 and m['height']<bx['height']-50 and abs((m['y']+m['height']/2)-(bx['y']+bx['height']/2))<1,f'파노라마 폭 맞춤·가운데 {m}')
    pg.screenshot(path=S+'thumb-pano.png')
print('FAILS',fails)
