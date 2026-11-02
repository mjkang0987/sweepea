# 개인정보 처리방침(138): 로그인 없이 열리고, 첫 화면·로그인·설정에서 링크, 책임자 연락처·시행일
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    r=pg.goto(B+'/privacy')
    check(r.status==200 and pg.get_by_role('heading',level=1).inner_text()=='개인정보 처리방침','로그인 없이 열림')
    t=pg.content()
    check('pikaworks.help@gmail.com' in t and 'PIKAWORKS' in t and '시행일' in t,'운영자·연락처·시행일')
    check(all(k in t for k in ['Supabase','Cloudflare','위치','3일','7일','118']),'맡기는 곳·위치 지움·보관 기간·구제 기관')
    check(pg.get_by_role('heading',level=2).count()>=10,'항목 제목(10개 이상)')
    pg.screenshot(path='/home/user/sweepea/tools/shots/privacy.png',full_page=False)
    for path in ['/','/login']:
        pg.goto(B+path); check(pg.get_by_role('link',name='개인정보 처리방침').count()==1,f'{path} 에서 처리방침 링크')
    pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings'); pg.get_by_role('link',name='개인정보 처리방침').click(); pg.wait_for_url('**/privacy')
    check(True,'설정에서 처리방침으로')
    b.close()
print('FAILS',FAILS)
