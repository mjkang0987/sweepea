from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    errs=[]
    pg.on('console', lambda m: errs.append((pg.url,m.type,m.text)) if m.type in ('error','warning') else None)
    pg.on('pageerror', lambda e: errs.append((pg.url,'pageerror',str(e))))
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    print('--- after upload', errs); errs.clear()
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pg.wait_for_timeout(800); print('view',errs); errs.clear()
    pg.locator('a[rel="next"]').click(); pg.wait_for_timeout(1500); print('next',errs); errs.clear()
    pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_timeout(1000); print('edit',errs); errs.clear()
    pg.go_back(); pg.wait_for_timeout(1000); print('back',errs); errs.clear()
    pg.get_by_role('link',name='닫기').first.click(); pg.wait_for_timeout(1000); print('close',errs); errs.clear()
    pg.goto(B+'/settings'); pg.wait_for_timeout(800); pg.locator('a[href^="/settings/"]').first.click(); pg.wait_for_timeout(1000); print('settings',errs)
    b.close()
