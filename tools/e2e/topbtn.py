# 위 버튼(닫기·뒤로) 자리 재기
import layerfix, json
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def box(pg,sel):
    return pg.locator(sel).first.evaluate("e=>{const b=e.getBoundingClientRect();const t=document.createRange();t.selectNodeContents(e);const r=[...t.getClientRects()].filter(x=>x.width>4).pop()||b;const cs=getComputedStyle(e);return {box:[Math.round(b.x),Math.round(b.y),Math.round(b.width),Math.round(b.height)],text:[Math.round(r.x),Math.round(r.y+r.height/2)],font:cs.fontSize,weight:cs.fontWeight,text_:e.textContent.trim()}}")
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    print('view 닫기', box(pg,'.sp-v__bar .sp-v__link'))
    pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    print('edit 닫기', box(pg,'.sp-p__back'))
    for path in ['/settings/storage','/settings/family','/upload','/reactions']:
        pg.goto(B+path)
        if pg.locator('.sp-p__back').count(): print(path, box(pg,'.sp-p__back'))
