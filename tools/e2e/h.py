from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844})
    pg.goto('http://localhost:4321/i/Harin001')
    print('who input/btn', pg.eval_on_selector('#who-name','e=>e.getBoundingClientRect().height'), pg.eval_on_selector('.sp-f__row .sp-f__btn','e=>e.getBoundingClientRect().height'), pg.eval_on_selector('.sp-f__name','e=>e.getBoundingClientRect().height'))
    pg.get_by_role('button',name='외할머니').click(); pg.wait_for_url('**/password**')
    print('pin/btn', pg.eval_on_selector('#pw','e=>e.getBoundingClientRect().height'), pg.eval_on_selector('.sp-f__bottom .sp-f__btn','e=>e.getBoundingClientRect().height'))
    b.close()
