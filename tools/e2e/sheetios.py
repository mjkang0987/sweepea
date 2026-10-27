# 한마디 시트: 목록 높이가 0으로 접히지 않고(사파리 버그 고침), 많으면 목록만 굴러감, 열면 초점은 제목
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':664}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    for i in range(2):
        pg.fill('#say-body',f'한마디 {i+1}'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    pg.locator('.sp-v__talk').click()
    h=pg.locator('.sp-v__sheet-list').evaluate('e=>e.getBoundingClientRect().height'); check(h>60,f'목록 2개 높이 {h}')
    check(pg.evaluate("document.activeElement.id")=='talk-title','열면 초점은 시트 제목(닫기 테두리 없음)')
    pg.screenshot(path=S+'sheet-2.png'); pg.keyboard.press('Escape')
    for i in range(10):
        pg.fill('#say-body',f'긴 목록 {i+1}'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    pg.locator('.sp-v__talk').click()
    r=pg.evaluate("()=>{const d=document.querySelector('#talk').getBoundingClientRect(),l=document.querySelector('.sp-v__sheet-list'),f=document.querySelector('.sp-v__sheet-form').getBoundingClientRect();return [d.height,innerHeight,l.scrollHeight>l.clientHeight,f.bottom<=innerHeight+1]}")
    check(r[0]<=r[1]*0.72+1 and r[2] and r[3],f'많으면 시트 72% 안에서 목록만 굴러감·입력칸 보임 {r}')
    pg.screenshot(path=S+'sheet-12.png')
print('FAILS',fails)
