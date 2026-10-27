from playwright.sync_api import sync_playwright
B='http://localhost:4321'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/storage'); print(pg.locator('.sp-p__card-title').inner_text())
