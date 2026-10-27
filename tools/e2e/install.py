# 홈 화면에 두기: 아이폰·안드로이드·카톡 안내, 다음에 할게요, 부탁하기 → 부모 최근 반응
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, "/home/claude/sweepea/tools/e2e"); import layerfix  # noqa
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
IOS='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
AND='Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36'
KAKAO=IOS+' KAKAOTALK 10.8.0'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    def enter(ua,name):
        c=b.new_context(viewport={'width':390,'height':844},user_agent=ua); pg=c.new_page(); pg.goto(B+'/i/Harin001')
        pg.get_by_role('button',name=name,exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
        return pg
    pg=enter(IOS,'외할머니')
    g=pg.get_by_role('complementary',name='홈 화면에 두세요'); check(g.count()==1 and '공유' in g.inner_text() and '홈 화면에 추가' in g.inner_text(),'아이폰 안내')
    pg.screenshot(path=D+'i-1.png')
    pg.get_by_role('button',name='다음에 할게요').click(); pg.wait_for_url('**/album**'); check(pg.get_by_role('complementary',name='홈 화면에 두세요').count()==0,'다음에 할게요 누르면 숨김')
    pa=enter(AND,'외할아버지'); g=pa.get_by_role('complementary',name='홈 화면에 두세요'); check('⋮' in g.inner_text(),'안드로이드 안내')
    pa.get_by_role('button',name='알겠어요').click(); pa.wait_for_url('**/album**'); check(pa.get_by_role('complementary',name='홈 화면에 두세요').count()==0,'알겠어요 누르면 숨김')
    pk=enter(KAKAO,'이모'); g=pk.get_by_role('complementary',name='홈 화면에 두세요'); check('앱 안에서는' in g.inner_text(),'카톡 안내')
    pk.screenshot(path=D+'i-2.png')
    pk.get_by_role('button',name='엄마아빠에게 부탁하기').click(); pk.wait_for_url('**/album**')
    check(pk.get_by_role('status').count()==1 and pk.get_by_role('complementary',name='홈 화면에 두세요').count()==0,'부탁하면 안내 숨기고 알림')
    pk.reload(); check(pk.get_by_role('status').count()==0,'알림은 한 번만')
    # 부모 쪽: 새 가족방에서 카톡으로 들어온 가족이 부탁 → 부모 최근 반응
    c=b.new_context(viewport={'width':390,'height':844}); pp=c.new_page()
    pp.goto(B+'/login'); pp.get_by_role('link',name='개발용으로 계속하기').click(); pp.wait_for_url('**/setup')
    pp.fill('#child','서아'); pp.fill('#birth','2025-09-17'); pp.get_by_role('button',name='다음').click(); pp.wait_for_url('**/setup/password**')
    pp.fill('#pw','0917'); pp.get_by_role('button',name='시작하기').click(); pp.wait_for_url('**/home')
    pp.goto(B+'/upload'); pp.set_input_files('#up-files',[D+'u0.jpg']); pp.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pp.get_by_role('button',name='보내지 않고 올리기만').click(); pp.wait_for_url('**/home',timeout=30000)
    pp.goto(B+'/settings/family'); pp.get_by_role('button',name='링크 만들기 (가족)').click(); pp.wait_for_selector('#link-url')
    code=pp.locator('#link-url').input_value().rsplit('/',1)[1]
    k=b.new_context(viewport={'width':390,'height':844},user_agent=KAKAO).new_page(); k.goto(B+'/i/'+code)
    k.fill('#who-name','할머니'); k.get_by_role('button',name='들어가기').click(); k.wait_for_url('**/password**'); k.fill('#pw','0917'); k.get_by_role('button',name='들어가기').click(); k.wait_for_url('**/wait')
    pp.goto(B+'/settings/family'); pp.get_by_role('button',name='승인 할머니').click(); pp.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    k.goto(B+'/album'); k.get_by_role('button',name='엄마아빠에게 부탁하기').click(); k.wait_for_url('**/album**')
    pp.goto(B+'/home'); al=pp.locator('.sp-p__alert'); check(al.count()==1 and '할머니가 홈 화면에 두기를 부탁했어요' in al.inner_text() and al.get_attribute('href')=='/settings/family/sms','부모 앨범 위 띠에 부탁 보임')
    pp.goto(B+'/reactions'); check('부탁' not in pp.locator('main').inner_text(),'최근 반응엔 부탁 없음')
    pp.screenshot(path=D+'i-3.png',full_page=True)
    pp.goto(B+'/'); check(pp.url.endswith('/home'),'부모가 홈 화면 아이콘(/)으로 열면 부모 앨범')
    # 이미 홈 화면에서 연 경우: display-mode standalone이면 CSS로 숨김
    ps=enter(IOS,'하린 아빠'); 
    hidden=ps.evaluate("""()=>{const s=document.createElement('style');s.textContent='';return getComputedStyle(document.querySelector('.sp-f__install')).display!=='none'}""")
    check(hidden,'일반 브라우저에선 보임')
    b.close()
print('ALL OK')
