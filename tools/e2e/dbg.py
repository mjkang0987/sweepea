from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name='외할머니',exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    sw="document.querySelector('.sp-a__swipe').scrollLeft"
    print('before',pg.evaluate(sw), pg.evaluate("window.scrollY"))
    pg.locator('#say-body-1').fill('x'); pg.wait_for_timeout(500)
    print('after',pg.evaluate(sw), pg.evaluate("window.scrollY"))
    print(pg.evaluate("(()=>{const r=document.querySelector('#say-1 button').getBoundingClientRect();const e=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return [r.x,r.y,r.width,e&&e.outerHTML.slice(0,80), getComputedStyle(document.querySelector('#say-1').closest('.sp-a__slide-react')).visibility]})()"))
    pg.screenshot(path=D+'dbg.png',full_page=True)
