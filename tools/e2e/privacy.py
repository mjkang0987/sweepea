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
    check('pikaworks.help@gmail.com' in t and 'PIKAWORKS' in t and '시행일' in t and '강지우' in t and '010-7188-0987' in t,'운영자·보호책임자(이름·전화·이메일)·시행일')
    check(all(k in t for k in ['Supabase','Cloudflare','위치','3일','7일','118','4032','3분']),'맡기는 곳·위치 지움·보관 기간·구제 기관·올리기 크기(141)')
    check(pg.get_by_role('heading',level=2).count()>=10,'항목 제목(10개 이상)')
    pg.screenshot(path='/home/user/sweepea/tools/shots/privacy.png',full_page=False)
    r=pg.goto(B+'/terms'); t2=pg.content()
    check(r.status==200 and pg.get_by_role('heading',level=1).inner_text()=='이용약관' and '원본은 따로 보관하지 않습니다' in t2 and '5GB' in t2 and '3일' in t2 and '2GB' in t2 and '3분' in t2,'이용약관: 로그인 없이, 원본 보관 안 함·5GB·탈퇴 3일·영상 2GB·3분 넘으면 그대로(141)')
    for path in ['/','/login']:
        pg.goto(B+path); check(pg.get_by_role('link',name='개인정보 처리방침').count()==1 and pg.get_by_role('link',name='이용약관').count()==1,f'{path} 에서 처리방침·이용약관 링크')
    pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings'); pg.get_by_role('link',name='개인정보 처리방침').click(); pg.wait_for_url('**/privacy**')
    check(True,'설정에서 처리방침으로')
    # 150: 맨 위 '뒤로'는 들어온 화면으로, 바로 열면 첫 화면으로
    check(pg.get_by_role('link',name='뒤로').get_attribute('href')=='/settings','처리방침 뒤로 → 설정')
    pg.get_by_role('link',name='뒤로').click(); pg.wait_for_url('**/settings')
    # 로그인한 채로는 /login이 앨범으로 넘어가서 새 창(로그인 전)으로
    n=b.new_context(viewport={'width':390,'height':844}).new_page()
    n.goto(B+'/login'); n.get_by_role('link',name='이용약관').click(); n.wait_for_url('**/terms**')
    check(n.get_by_role('link',name='뒤로').get_attribute('href')=='/login','약관 뒤로 → 로그인')
    n.goto(B+'/terms'); check(n.get_by_role('link',name='뒤로').get_attribute('href')=='/','바로 열면 뒤로 → 첫 화면')
    b.close()
print('FAILS',FAILS)
