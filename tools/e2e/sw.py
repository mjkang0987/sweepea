import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/shots/'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','하린 아빠'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings'); pg.screenshot(path=D+'c_settings_badge.png',full_page=True)
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 하린 아빠').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    pg.get_by_role('link',name='하린 아빠').click(); pg.wait_for_url('**/member/**'); pg.screenshot(path=D+'c_member.png',full_page=True)
    pg.goto(B+'/settings'); pg.screenshot(path=D+'c_settings.png',full_page=True)
    pg.goto(B+'/settings/account'); pg.screenshot(path=D+'c_account.png')
    pg.goto(B+'/settings/storage'); pg.screenshot(path=D+'c_storage.png')
    pg.goto(B+'/settings/family/groups'); pg.screenshot(path=D+'c_groups.png')
