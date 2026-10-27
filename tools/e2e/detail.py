from playwright.sync_api import sync_playwright
B='http://localhost:4321'
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name='외할아버지',exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    pg.locator('.sp-a__card-link').first.click(); pg.wait_for_load_state(); pg.wait_for_timeout(300)
    pg.screenshot(path='/home/claude/sweepea/tools/e2e/detail.png',full_page=True)
    b.close()
