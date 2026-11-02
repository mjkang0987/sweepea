# 크게 보기 미리 받기(131): 누르기 시작하면 브라우저가 크게 보기를 미리 받고(크롬 계열 speculationrules), 미리 받기만으로는 '봤음'이 안 남음, 실제로 열면 남음
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/user/sweepea/tools/e2e/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
# 방금(3시간 안) 올라온 안 본 사진은 맨 위 '방금 올라왔어요' 묶음에 있다(보면 제자리로)
NEW='.sp-a__day[data-day="new"] .sp-a__cell'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 이모').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+'/album')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    gp.goto(B+'/album?v=list&z=3'); check(gp.locator(NEW).count()==2,'신규 2장')
    links=gp.locator('.sp-a__day[data-day="new"] .sp-a__cell-link')
    # 1) 누르기 시작만(놓지 않고 다른 데로): 미리 받기는 돼도 '봤음'은 안 남음
    box=links.nth(1).bounding_box(); gp.mouse.move(box['x']+20,box['y']+20); gp.mouse.down(); gp.wait_for_timeout(1200); gp.mouse.move(5,5); gp.mouse.up(); gp.wait_for_timeout(300)
    gp.reload(); check(gp.locator(NEW).count()==2,"미리 받기만 하고 안 열면 '봤음' 안 남음(신규 2장 그대로)")
    # 2) 누르고 열기: 미리 받은 화면이면 그대로 쓰이고, 열린 화면이 '봤음'을 남김
    box=links.nth(0).bounding_box(); gp.mouse.move(box['x']+20,box['y']+20); gp.mouse.down(); gp.wait_for_timeout(600); gp.mouse.up(); gp.wait_for_url('**/album/**'); gp.wait_for_timeout(800)
    dt=gp.evaluate("performance.getEntriesByType('navigation')[0].deliveryType")
    print('deliveryType:',repr(dt))
    check(dt=='navigational-prefetch','열린 크게 보기는 미리 받은 화면')
    gp.goto(B+'/album?v=list&z=3'); check(gp.locator(NEW).count()==1,"열면 '봤음' 남음(신규 1장)")
    b.close()
print('FAILS',FAILS)
