# 동의 받기(152): 처음 설정 필수 체크·직접 주소로 오면 1단계로, 가족 입장 안내, 건강 정보 동의 없이 저장 막기 (초대받은 엄빠 /agree는 coparent.py, 건강 동의 화면은 health.py)
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); check('처음 시작할 때' in pg.content(),'로그인: 동의는 처음 시작할 때 받는다는 안내')
    pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    check(pg.locator('input[name=agree_terms][required]').count()==1 and pg.locator('input[name=agree_privacy][required]').count()==1,'1단계에 필수 체크 칸 둘')
    check('from=%2Fsetup' in pg.get_by_role('link',name='보기 이용약관').get_attribute('href'),"'보기'는 설정으로 돌아오는 약관 링크")
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click()
    check('/setup/password' not in pg.url,'체크 안 하면 브라우저가 막음(2단계로 안 감)')
    pg.goto(B+'/setup/password?child=하린&birth=2025-09-17&role=mom'); pg.wait_for_url('**e=agree**')
    check('필수 항목에 모두 동의해 주세요' in pg.content() and '생일을 골라 주세요' not in pg.content(),'직접 주소로 오면 1단계로 + 동의 안내만')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/agree'); check(pg.url.endswith('/home'),'동의한 엄빠가 /agree로 오면 앨범으로')
    kid=pg.goto(B+'/settings/children') and pg.locator('a[href^="/health/"]').first.get_attribute('href').split('?')[0]
    r=pg.request.post(B+kid,form={'shown':'hepb1','done':'hepb1'}); check('done=need' in r.url,'건강 정보 동의 없이 보내면 저장 안 함')
    f=b.new_context(viewport={'width':390,'height':844}).new_page(); f.goto(B+'/i/Harin001')
    note=f.locator('.sp-f__fine'); check(note.count()==1 and '개인정보 처리방침' in note.inner_text() and note.get_by_role('link').get_attribute('href').startswith('/privacy?from='),'가족 입장: 처리방침 안내·링크')
    b.close()
print('FAILS',FAILS)
