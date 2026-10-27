# 문자로 공유하기: 들어온 가족 없을 때 빈 상태(콩이·제목·설명·버튼)
import layerfix
from playwright.sync_api import sync_playwright
from PIL import Image
B='http://localhost:4321'; S='/home/claude/sweepea/tools/shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family/sms')
    check(pg.get_by_role('heading',name='아직 들어온 가족이 없어요').count()==1,'빈 상태 제목')
    lead=pg.locator('.sp-p__lead').first.evaluate('e=>getComputedStyle(e).fontSize'); txt=pg.locator('.sp-p__empty .sp-p__lead').evaluate('e=>getComputedStyle(e).fontSize')
    check(lead==txt,f'안내문·설명 같은 크기 {lead} {txt}')
    btn=pg.get_by_role('link',name='가족 링크 보내러 가기'); check(btn.get_attribute('href')=='/settings/family','버튼 → 가족')
    bb=btn.bounding_box(); check(bb['width']>=340 and bb['height']>=44,f'버튼 폭 가득 {bb}')
    check('설치 링크' in pg.locator('.sp-p__lead').first.inner_text(),'안내문 디자인 문구')
    pg.screenshot(path=S+'sms-empty.png')
    d=b.new_context(viewport={'width':390,'height':844},color_scheme='dark'); d.add_cookies(c.cookies()); dp=d.new_page(); dp.goto(B+'/settings/family/sms'); dp.screenshot(path=S+'sms-empty-d.png')
print('FAILS',fails)
