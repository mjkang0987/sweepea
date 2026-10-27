# 홈 가운데 레이어 그 자리에서(74): 모달로 올리고 닫기·나중에·Esc는 페이지 이동 없이, 여러 개면 하나씩(들어오기 신청 → 백일 → 저장 공간).
# 저장 공간까지 보려면 개발 서버를 SWEEPEA_MOCK_USED_BYTES=4939212390(약 92%)로 띄운다 (mock)
import os,datetime
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'; O=D+'../shots/hl-'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
T=(datetime.datetime.utcnow()+datetime.timedelta(hours=9)).date(); D100=str(T-datetime.timedelta(days=99))
def title(pg): return pg.locator('dialog[open] .sp-layer__title').inner_text() if pg.locator('dialog[open]').count() else ''
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth',D100); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    # 들어오기 신청 하나 만들기
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    x=b.new_context().new_page(); x.goto(B+'/i/'+code); x.fill('#who-name','외할머니'); x.get_by_role('button',name='들어가기').click(); x.wait_for_url('**/password**'); x.fill('#pw','0917'); x.get_by_role('button',name='들어가기').click(); x.wait_for_url('**/wait')
    pg.goto(B+'/home'); pg.evaluate('window.__same=1')
    check(pg.locator('dialog[open]').count()==1 and '외할머니' in title(pg),'처음엔 들어오기 신청 레이어 하나(모달, 한 번에 하나)')
    check(pg.evaluate("document.querySelector('dialog[open]').matches(':modal')"),'모달로 올라감')
    check(pg.evaluate("document.activeElement.textContent.trim()")=='확인하기','첫 버튼에 초점')
    for _ in range(4): pg.keyboard.press('Tab')
    check(pg.evaluate("!!document.activeElement.closest('dialog[open]')"),'Tab이 레이어 밖으로 안 나감')
    pg.screenshot(path=O+'join.png')
    # Esc = 나중에: 그 자리에서, 다음은 백일
    with pg.expect_response(lambda r: r.request.method=='POST' and r.status==204): pg.keyboard.press('Escape')
    check(pg.evaluate('window.__same')==1 and '100일' in title(pg) and pg.locator('dialog[open]').count()==1,'Esc → 나중에처럼 닫히고 그 자리에서 백일 레이어')
    check(pg.evaluate("document.activeElement.textContent.trim()")=='사진 올리기','다음 레이어 첫 버튼에 초점')
    with pg.expect_response(lambda r: r.request.method=='POST' and r.status==204): pg.locator('dialog[open]').get_by_role('button',name='닫기').click()
    nxt=title(pg)
    check(pg.evaluate('window.__same')==1 and ('저장 공간' in nxt or nxt==''),'닫기 → 그 자리에서(저장 공간 레이어가 있으면 다음)')
    if nxt:
        with pg.expect_response(lambda r: r.request.method=='POST' and r.status==204): pg.locator('dialog[open]').get_by_role('button',name='나중에').click()
    check(pg.locator('dialog[open]').count()==0 and pg.evaluate("document.activeElement.classList.contains('sp-p__title')"),'다 닫으면 화면 제목으로 초점')
    check(pg.locator('.sp-p__alert').count()==1,'들어오기 신청 띠는 남음')
    pg.reload(); check(pg.locator('.sp-layer').count()==0,'다시 열어도 레이어 없음(봤음 적힘)')
    # 다른 화면 가는 버튼은 이동
    y=b.new_context().new_page(); y.goto(B+'/i/'+code); y.fill('#who-name','큰이모'); y.get_by_role('button',name='들어가기').click(); y.wait_for_url('**/password**'); y.fill('#pw','0917'); y.get_by_role('button',name='들어가기').click(); y.wait_for_url('**/wait')
    pg.goto(B+'/home'); pg.locator('dialog[open]').get_by_role('button',name='확인하기').click(); pg.wait_for_url('**/settings/family')
    check(True,'확인하기 → 가족 설정으로 이동')
    # 스크립트 없이: 예전처럼 폼
    z=b.new_context().new_page(); z.goto(B+'/i/'+code); z.fill('#who-name','고모'); z.get_by_role('button',name='들어가기').click(); z.wait_for_url('**/password**'); z.fill('#pw','0917'); z.get_by_role('button',name='들어가기').click(); z.wait_for_url('**/wait')
    q=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=c.storage_state()).new_page()
    q.goto(B+'/home'); check('고모' in q.locator('.sp-layer:not([hidden]) .sp-layer__title').first.inner_text(),'스크립트 없어도 레이어')
    q.wait_for_timeout(600); q.locator('.sp-layer:not([hidden])').get_by_role('button',name='나중에').click(); q.wait_for_load_state()
    check(q.locator('.sp-layer:not([hidden]) .sp-layer__title',has_text='고모').count()==0,'스크립트 없으면 폼으로 닫힘')
    b.close()
print('FAILS',FAILS)
