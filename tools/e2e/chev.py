# 뒤로 링크에 ‹ 표시, 취소 링크엔 없음
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; S='/home/claude/sweepea/tools/shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    for path,name in [('/settings/storage','설정'),('/settings/family','설정'),('/settings/text-size','설정')]:
        pg.goto(B+path); a=pg.locator('.sp-p__back').first
        w=a.evaluate("e=>getComputedStyle(e,'::before').width")
        check(a.inner_text().strip()==name and w not in ('auto','0px'),f'{path} 뒤로 ‹ {w}')
    pg.screenshot(path=S+'chev-code.png',clip={'x':0,'y':0,'width':390,'height':120})
    pg.goto(B+'/upload'); a=pg.locator('.sp-p__back').first
    check(a.evaluate("e=>getComputedStyle(e,'::before').content")=='none','올리기 취소엔 ‹ 없음')
print('FAILS',fails)
