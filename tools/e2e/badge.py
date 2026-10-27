import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    tab=lambda: pg.locator('.sp-p__tabs a[href="/settings"]')
    check(tab().get_attribute('aria-label') is None and tab().locator('.sp-p__tab-badge').count()==0,'처음엔 배지 없음')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','큰이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings')
    check(tab().get_attribute('aria-label')=='설정, 승인 기다리는 사람 1명','설정 탭 이름에 수')
    check(tab().locator('.sp-p__tab-badge').inner_text()=='1','설정 탭 배지 1')
    pg.screenshot(path=D+'badge-settings.png')
    pg.goto(B+'/reactions'); check(tab().locator('.sp-p__tab-badge').count()==1,'알림 화면에서도 배지')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 큰이모').click(); pg.wait_for_url('**done=member-active**')
    check(tab().locator('.sp-p__tab-badge').count()==0,'승인하면 배지 사라짐')
print('FAILS',fails)
