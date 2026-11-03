# 가족 글자 크기(149): 앨범 머리 '글자 크기' → 고르고 저장 → 앨범·이 화면이 그 크기, 스크립트 없이도
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    for js in (True, False):
        # 들어가기는 스크립트를 켠 채로 하고, 글자 크기 화면은 js 그대로(스크립트 없이도 되는지)
        e=b.new_context(viewport={'width':390,'height':844}); q=e.new_page()
        q.goto(B+'/i/Harin001'); q.get_by_role('button',name='외할머니',exact=True).click(); q.wait_for_url('**/password**')
        q.fill('#pw','1234'); q.get_by_role('button',name='들어가기').click(); q.wait_for_url('**/album')
        c=b.new_context(viewport={'width':390,'height':844},java_script_enabled=js); c.add_cookies(e.cookies()); e.close()
        pg=c.new_page(); pg.goto(B+'/album')
        cls=lambda: pg.evaluate('document.documentElement.className')
        check('sp-size-large' in cls(),f'외할머니는 크게로 시작(js={js})')
        link=pg.get_by_role('link',name='글자 크기'); check(link.get_attribute('href')=='/me/text-size','앨범 머리에 글자 크기')
        # 스크립트 없는 headless 크롬은 화면 전환(view transition)이 남아 클릭을 가로채서 주소로 연다(다른 no-JS 검사와 같이)
        (link.click() if js else pg.goto(B+'/me/text-size')); pg.wait_for_url('**/me/text-size')
        check(pg.get_by_role('radio',name='크게',exact=True).is_checked(),'지금 크기(크게)가 골라져 있음')
        pg.get_by_text('아주 크게',exact=True).click(); pg.get_by_role('button',name='저장').click(); pg.wait_for_url('**done=saved**')
        check('sp-size-xlarge' in cls() and '글자 크기를 바꿨어요' in pg.content(),'저장하면 이 화면이 바로 아주 크게 + 토스트')
        (pg.get_by_role('link',name='앨범').first.click() if js else pg.goto(B+'/album')); pg.wait_for_url('**/album**')
        check('sp-size-xlarge' in cls(),'앨범도 아주 크게')
        c.close()
    r=b.new_context().new_page(); r.goto(B+'/me/text-size'); check(r.url.rstrip('/')==B,'출입증 없으면 첫 화면으로')
    b.close()
print('FAILS',FAILS)
