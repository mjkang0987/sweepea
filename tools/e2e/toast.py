# 토스트: 보냄(하트·반짝)·오류(느낌표) 카드가 판 위에 떴다가 사라짐, 주소에서 say 뗌, 동작 줄이기
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); vid=pg.url.split('/view/')[1].split('?')[0]
    # 빈 한마디 → 오류 토스트
    pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')"); pg.wait_for_timeout(150)
    t=pg.locator('.sp-toast'); check(pg.locator('.sp-v > [role=alert].sp-vh').inner_text()=='한마디를 써 주세요.' and '한마디를 써 주세요.' in t.inner_text(),'빈 한마디: 오류 토스트')
    check('say=' not in pg.url and 'sm=' not in pg.url,f'주소에서 결과 표시 뗌 {pg.url}')
    pg.wait_for_timeout(500); tb=t.bounding_box(); pb=pg.locator('.sp-v__dock').bounding_box()
    check(abs(pb['y']-(tb['y']+tb['height'])-12)<=1 and tb['x']>=19 and tb['height']>=60,f'판 바로 위에 뜸 {tb} {pb}')
    check(pg.locator('.sp-f__box').count()==0,'입력칸 아래 상자 없음')
    pg.screenshot(path=S+'toast-err.png')
    pg.wait_for_timeout(6300); check(not t.is_visible(),'6초 뒤 사라짐')
    pg.fill('#say-body','잘 봤어'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')"); pg.wait_for_timeout(150)
    t=pg.locator('.sp-toast'); check('보냈어요' in pg.locator('.sp-v > [role=status].sp-vh').inner_text(),'보냄 토스트')
    pg.wait_for_timeout(300); pg.screenshot(path=S+'toast-ok.png')
    pg.wait_for_timeout(4200); check(not t.is_visible(),'4초 뒤 사라짐')
    pg.reload(); check(pg.locator('.sp-toast').count()==0,'새로 고침하면 다시 안 뜸')
    # 동작 줄이기: 움직임 없이 나타났다 사라짐
    rm=b.new_context(viewport={'width':390,'height':844},reduced_motion='reduce'); rm.add_cookies(c.cookies()); r=rm.new_page(); r.goto(B+'/view/'+vid)
    r.locator('#say').get_by_role('button',name='보내기').click(); r.wait_for_selector('.sp-toast')
    check(r.locator('.sp-toast').evaluate('e=>getComputedStyle(e).animationName')=='sp-toast-card-still','동작 줄이기: 움직임 없는 사라짐')
    d=b.new_context(viewport={'width':390,'height':844},color_scheme='dark'); d.add_cookies(c.cookies()); dp=d.new_page(); dp.goto(B+'/view/'+vid)
    dp.fill('#say-body','다크'); dp.locator('#say').get_by_role('button',name='보내기').click(); dp.wait_for_selector('.sp-toast'); dp.wait_for_timeout(300); dp.screenshot(path=S+'toast-ok-d.png')
print('FAILS',fails)
