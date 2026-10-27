# 탈퇴하기 → 가족 화면 닫힘·작별 → 다시 로그인 → 되살리기 / 그대로 탈퇴하기
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    shots=[]
    def shot(n): pg.screenshot(path=D+'d-'+n+'.png',full_page=True)
    def login():
        pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_load_state()
    login(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 이모').click(); pg.wait_for_url('**done=member-active**')
    gp.goto(B+'/album'); check(gp.locator('.sp-a__card-link').count()>=1,'가족 앨범 열림')
    # 탈퇴. mock은 로그인할 때마다 새 사용자라, '같은 사람이 다시 로그인'은 부모 쿠키를 되돌려 흉내 낸다
    saved=[x for x in c.cookies() if x['name']=='sp_parent']
    def relogin(): c.add_cookies(saved); pg.goto(B+'/home')
    pg.goto(B+'/settings/account'); pg.get_by_role('link',name='탈퇴하기').click(); pg.wait_for_url('**confirm=delete**')
    check('사진 1장과' in pg.content(),'확인에 사진 수'); shot('1')
    pg.evaluate("document.querySelector('[name=agree]').removeAttribute('required')")
    pg.get_by_role('button',name='탈퇴하기').click(); pg.wait_for_url('**confirm=delete**')
    check(pg.get_by_role('alert').count()==1 and pg.get_by_label('모두 지워지는 것을 확인했어요').get_attribute('aria-invalid')=='true','체크 안 하면 이유와 함께 다시 확인')
    pg.get_by_label('모두 지워지는 것을 확인했어요').check(); pg.get_by_role('button',name='탈퇴하기').click(); pg.wait_for_url('**/goodbye?on=**')
    check('그동안 고마웠어요' in pg.content() and '월' in pg.locator('.sp-p__lead').inner_text(),'작별 화면에 지울 날'); shot('2')
    pg.goto(B+'/home'); check('/login' in pg.url or '/start' in pg.url,'탈퇴하면 로그아웃')
    gp.goto(B+'/album'); check(gp.locator('.sp-a__card-link').count()==0,'가족 화면은 바로 닫힘')
    # 다시 로그인 → 그대로 탈퇴하기
    relogin(); pg.wait_for_url('**/restore'); check('탈퇴 신청 중이에요' in pg.content(),'다시 로그인하면 되살리기 화면'); check(pg.locator('.sp-p__remaining').inner_text() in ('2일 23시간 남았어요','3일 남았어요'),'남은 시간 안내 ('+pg.locator('.sp-p__remaining').inner_text()+')'); shot('3')
    pg.goto(B+'/settings'); check(pg.url.endswith('/restore'),'유예 중엔 다른 부모 화면 막힘')
    pg.get_by_role('button',name='그대로 탈퇴하기').click(); pg.wait_for_url('**/goodbye?on=**'); check(True,'그대로 탈퇴하기는 작별 화면')
    # 다시 로그인 → 되살리기
    relogin(); pg.wait_for_url('**/restore'); pg.get_by_role('button',name='되살리기').click(); pg.wait_for_url('**/home')
    check(True,'되살리면 앨범으로')
    gp.goto(B+'/album'); check(gp.locator('.sp-a__card-link').count()>=1,'되살리면 가족 화면 다시 열림')
    pg.goto(B+'/restore'); check(pg.url.endswith('/home'),'유예가 아니면 되살리기 화면 안 열림')
    for q in ['2026-13-45','x','']:
        pg.goto(B+'/goodbye?on='+q); check('3일 뒤 사진과' in pg.content(),'이상한 날짜는 3일 뒤로 ('+q+')')
    b.close()
print('ALL OK')
