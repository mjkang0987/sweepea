from playwright.sync_api import sync_playwright
import sys
B='http://localhost:4321'
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',['u0.jpg','u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/photo/**')
    pg.evaluate("""()=>{for(const t of ['pointerdown','pointerup','pointercancel','dragstart'])document.addEventListener(t,e=>console.log(t,e.target.className),true)}""")
    pg.on('console',lambda m:print('C',m.text))
    print(pg.locator('script').evaluate_all('e=>e.map(s=>s.src||s.textContent.slice(0,60))'))
    box=pg.locator('[data-stage]').bounding_box(); print(box); y=box['y']+box['height']*0.3; cx=box['x']+box['width']/2
    pg.mouse.move(cx+110,y); pg.mouse.down(); pg.mouse.move(cx-110,y,steps=5); pg.mouse.up(); pg.wait_for_timeout(1500); print(pg.url)
