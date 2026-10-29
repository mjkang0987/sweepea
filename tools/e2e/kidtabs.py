import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S='/home/claude/sweepea/tools/shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def up(pg,f,kid):
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.locator('label',has_text=kid).locator('input[name=child]').check()
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    check(pg.locator('.sp-p__seg').count()==0,'아이 하나면 탭 없음')
    pg.goto(B+'/settings/children/new'); pg.fill('#name','도윤'); pg.fill('#birth','2023-03-02'); pg.get_by_role('button',name='추가').click(); pg.wait_for_load_state()
    up(pg,'u0.jpg','하린'); up(pg,'u1.jpg','도윤')
    seg=pg.get_by_role('navigation',name='아이 고르기')
    check(seg.get_by_role('link').count()==3,'탭 3개(전체·하린·도윤)')
    check(seg.get_by_role('link',name='전체').get_attribute('aria-current')=='page','처음엔 전체')
    check(pg.locator('.sp-p__cell').count()==2,'전체 2장')
    sw=seg.bounding_box()['width']; mw=pg.locator('main').bounding_box()['width']
    check(sw>mw-60,'폰은 가로 꽉')
    pg.screenshot(path=S+'kid-phone.png')
    seg.get_by_role('link',name='하린').click(); pg.wait_for_url('**k=**')
    check(pg.locator('.sp-p__cell').count()==1,'하린 1장')
    check(pg.get_by_role('navigation',name='아이 고르기').get_by_role('link',name='하린').get_attribute('aria-current')=='page','하린 선택 표시')
    pg.get_by_role('navigation',name='아이 고르기').get_by_role('link',name='도윤').click(); pg.wait_for_url('**k=**')
    check(pg.locator('.sp-p__cell').count()==1,'도윤 1장')
    pg.goto(B+'/home?k=nope'); check(pg.locator('.sp-p__cell').count()==2,'모르는 값이면 전체')
    pg.set_viewport_size({'width':1280,'height':800}); pg.goto(B+'/home')
    seg=pg.get_by_role('navigation',name='아이 고르기')
    check(seg.bounding_box()['width']<400,'PC는 글자 폭만큼')
    pg.screenshot(path=S+'kid-pc.png')
print('FAILS',fails)
