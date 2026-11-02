# 사진 주소 캐시(135): 다시 열어도 같은 주소(6시간 단위), /m 응답 캐시는 6~12시간, 엉터리 만료는 404
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/user/sweepea/tools/e2e/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=30000)
    pg.goto(B+'/home?v=list&z=3'); s1=pg.locator('.sp-p__cell-img').first.get_attribute('src')
    pg.reload(); s2=pg.locator('.sp-p__cell-img').first.get_attribute('src')
    check(s1==s2,'다시 열어도 같은 사진 주소(브라우저 캐시를 씀)')
    r=pg.context.request.get(B+s1)
    cc=r.headers.get('cache-control',''); age=int(cc.split('max-age=')[1]) if 'max-age=' in cc else -1
    check(r.status==200 and 6*3600 < age <= 12*3600,f'사진 응답 캐시 6~12시간 ({cc})')
    e=int(s1.split('e=')[1].split('&')[0])
    bad=s1.replace(f'e={e}',f'e={e+13*3600}')
    check(pg.context.request.get(B+bad).status==404,'만료를 늘려 고친 주소는 404(서명·범위)')
    b.close()
print('FAILS',FAILS)
