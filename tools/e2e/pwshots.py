from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.screenshot(path=D+'pw-setup.png')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family/groups/new'); pg.screenshot(path=D+'pw-new.png')
    pg.goto(B+'/settings/family/groups'); pg.locator('.sp-p__row',has_text='가족').first.click(); pg.wait_for_url('**/groups/*'); pg.screenshot(path=D+'pw-detail.png',full_page=True)
    pg.locator('a[href$="/password"]').click(); pg.wait_for_url('**/password'); pg.fill('#pw','12'); pg.screenshot(path=D+'pw-change.png')
