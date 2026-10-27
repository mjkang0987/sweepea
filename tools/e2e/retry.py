# 올리다 끊기면 다시 눌러 이어 올리기(중복 없음)
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload')
    pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    state={'n':0}
    def fail_once(route):
        state['n']+=1
        if state['n']==3: route.abort()
        else: route.continue_()
    pg.route('**/api/media/*/view',fail_once)
    pg.get_by_role('button',name='보내지 않고 올리기만').click()
    pg.wait_for_function("document.getElementById('up-status').textContent.includes('이어서')",timeout=30000)
    check('2장까지 올렸어요' in pg.locator('#up-status').text_content(),'끊기면 몇 장까지 올렸는지 안내')
    pg.unroute('**/api/media/*/view')
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    check(pg.locator('.sp-p__cell').count()==3,'다시 눌러도 중복 없이 3장')
    b.close()
print('ALL OK')
