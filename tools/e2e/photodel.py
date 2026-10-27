# 사진 지우기 레이어: 스크립트 있으면 showModal(주소 그대로), 취소·Esc·바깥으로 닫힘, 지우기 → 홈. 스크립트 없으면 ?confirm=delete로 같은 레이어
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pc=b.new_context(viewport={'width':390,'height':844}); pg=pc.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u0.jpg',D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    n0=pg.locator('.sp-p__cell-link').count()
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); vid=pg.url.split('/view/')[1].split('?')[0]
    pg.goto(B+'/photo/'+vid); u=pg.url
    check(not pg.locator('#del').is_visible(),'처음엔 레이어 숨김')
    pg.get_by_role('link',name='사진 지우기').click()
    check(pg.evaluate("document.getElementById('del').matches(':modal')") and pg.url==u,'누르면 레이어(페이지 이동 없음)')
    check(pg.get_by_role('heading',name='이 사진을 지울까요?').is_visible(),'제목')
    check(pg.evaluate("document.activeElement.textContent.trim()")=='취소','포커스는 취소')
    pg.wait_for_timeout(500); db=pg.locator('#del').bounding_box(); check(abs(db['x']-20)<=1 and abs(db['x']+db['width']-370)<=1,f'좌우 20px {db}')
    check(abs((db['y']+db['height']/2)-422)<=2,f'세로 가운데 {db}')
    pg.wait_for_timeout(400); pg.screenshot(path=S+'photodel.png')
    pg.get_by_role('button',name='취소').click(); check(not pg.locator('#del').is_visible(),'취소로 닫힘')
    pg.get_by_role('link',name='사진 지우기').click(); pg.keyboard.press('Escape'); check(not pg.locator('#del').is_visible(),'Esc로 닫힘')
    pg.get_by_role('link',name='사진 지우기').click(); pg.mouse.click(195,60); check(not pg.locator('#del').is_visible(),'바깥 누르면 닫힘')
    check(pg.evaluate("document.activeElement?.hasAttribute('data-del-open')"),'닫으면 지우기 링크로 포커스')
    pg.get_by_role('link',name='사진 지우기').click(); pg.locator('#del').get_by_role('button',name='지우기').click(); pg.wait_for_url('**/home**')
    check('done=deleted' in pg.url and pg.locator('.sp-p__cell-link').count()==n0-1,'지우면 홈·한 장 줄어듦')
    # 스크립트 없음
    nc=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=pc.storage_state()); q=nc.new_page()
    q.goto(B+'/home'); href=q.locator('.sp-p__cell-link').first.get_attribute('href'); pid=href.split('/view/')[1].split('?')[0]
    q.goto(B+'/photo/'+pid); q.get_by_role('link',name='사진 지우기').click(); q.wait_for_url('**confirm=delete**')
    check(q.locator('.sp-layer .sp-layer__box').is_visible() and q.get_by_role('heading',name='이 사진을 지울까요?').is_visible(),'스크립트 없이: 같은 레이어')
    q.wait_for_timeout(1500); q.screenshot(path=S+'photodel-nojs.png')
    q.get_by_role('link',name='취소').click(force=True); q.wait_for_url('**/photo/*'); q.wait_for_timeout(600); check('confirm' not in q.url and q.locator('.sp-layer').count()==0,'스크립트 없이: 취소')
    # 스크립트 없는 창에서 Playwright 안정 검사가 페이지 전환 뒤 멈춰 force로 누름(실사용과 무관)
    q.get_by_role('link',name='사진 지우기').click(force=True); q.wait_for_url('**confirm=delete**'); q.wait_for_timeout(600); q.get_by_role('button',name='지우기').click(force=True); q.wait_for_url('**/home**')
    check(q.locator('.sp-p__cell-link').count()==n0-2,'스크립트 없이: 지우기')
    b.close()
print('FAILS',fails)
