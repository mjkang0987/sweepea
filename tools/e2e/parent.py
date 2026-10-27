# 부모 시작 흐름 (mock)
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; O='/home/claude/sweepea/tools/e2e/p-'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
shots=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    def shot(n): pg.screenshot(path=O+n+'.png'); shots.append(O+n+'.png')
    pg.goto(B+'/home'); check(pg.url.endswith('/start'),'로그인 전 첫 방문은 소개로'); shot('1')
    pg.get_by_role('link',name='다음').click(); pg.wait_for_url('**p=2'); shot('2')
    pg.get_by_role('link',name='다음').click(); pg.wait_for_url('**p=3'); shot('3')
    check(pg.get_by_role('link',name='건너뛰기').count()==0,'마지막 장엔 건너뛰기 없음')
    pg.get_by_role('link',name='시작하기').click(); pg.wait_for_url('**/login'); shot('4')
    check(pg.get_by_role('link',name='카카오로 계속하기').count()==0,'켜지 않은 제공자는 숨김')
    pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    check(True,'로그인 뒤 설정 전이면 처음 설정으로'); 
    pg.goto(B+'/setup/password?child=x&birth=2025-02-31&role=mom'); check(pg.url.endswith('e=birth'),'없는 날짜(2월 31일)는 1단계로')
    pg.goto(B+'/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_label('아빠').check(); shot('5')
    pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','12'); pg.evaluate("document.querySelector('#pw').removeAttribute('pattern');document.querySelector('#pw').removeAttribute('required')")
    pg.get_by_role('button',name='시작하기').click(); pg.wait_for_load_state()
    check('숫자 4자리를 써 주세요' in pg.content(),'4자리 아니면 안내')
    pg.fill('#pw','0917'); pg.fill('#hint','0917 생일'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_load_state()
    check('힌트에 비밀번호를' in pg.content(),'힌트에 비밀번호 그대로면 안내')
    pg.fill('#pw','0917'); pg.fill('#hint','서아 생일'); shot('6')
    pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    check('서아 첫 사진을 올려 주세요' in pg.content(),'빈 앨범'); shot('7')
    pg.goto(B+'/setup'); check(pg.url.endswith('/home'),'설정 끝난 부모는 처음 설정 대신 앨범')
    pg.goto(B+'/setup/password?child=x&birth=2025-01-01&role=mom'); check(pg.url.endswith('/home'),'2단계도 앨범으로')
    pg.goto(B+'/login'); check(pg.url.endswith('/home'),'로그인한 부모는 로그인 화면 대신 앨범')
    pg.get_by_role('link',name='설정').click(); pg.wait_for_url('**/settings')
    pg.goto(B+'/settings/account'); pg.get_by_role('button',name='로그아웃').click(); pg.wait_for_url('**/login')
    pg.goto(B+'/home'); check(pg.url.endswith('/login'),'로그아웃 뒤엔 소개 대신 로그인')
    r=c.request.get(B+'/login/kakao',max_redirects=0); check(r.status==302 and r.headers['location']=='/login','켜지 않은 제공자 주소는 로그인으로')
    r=c.request.get(B+'/auth/callback?code=dev-x',max_redirects=0); check(r.headers['location']=='/login?e=1','PKCE 쿠키 없이 돌아오면 실패')
    pg.goto(B+'/login?e=1'); check('로그인하지 못했어요' in pg.content(),'실패 안내')
    # 가족 기기 출입증과 섞이지 않음
    pg.goto(B+'/album'); check(pg.url.endswith('/'),'부모 세션으로 가족 앨범엔 안 들어감')
    b.close()
from PIL import Image
ims=[Image.open(x) for x in shots]
o=Image.new('RGB',(sum(i.width for i in ims)+10*len(ims),ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(O+'all.png'); print('ALL OK')
