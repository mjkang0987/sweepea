from playwright.sync_api import sync_playwright
B='http://localhost:4321'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name='이모',exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album**')
    print(pg.url, pg.locator('.sp-a__slide').count(), pg.locator('.sp-h__btn').count())
    pg.screenshot(path='../shots/dbgr.png')
