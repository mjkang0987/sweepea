# 가족 한 명 그 자리에서(75): 사진 올리기 허용 스위치는 페이지 이동 없이 + 토스트, 내보내기 확인은 이 화면 위 레이어 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; O=os.path.dirname(os.path.abspath(__file__))+'/../shots/mp-'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
def live(pg,word): pg.wait_for_function("document.getElementById('mem-live')?.textContent.includes(%r)"%word)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    x=b.new_context().new_page(); x.goto(B+'/i/'+code); x.fill('#who-name','서아 아빠'); x.get_by_role('button',name='들어가기').click(); x.wait_for_url('**/password**'); x.fill('#pw','0917'); x.get_by_role('button',name='들어가기').click(); x.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 서아 아빠').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    pg.get_by_role('link',name='서아 아빠').click(); pg.wait_for_url('**/member/**'); url=pg.url; pg.evaluate('window.__same=1')
    sw=pg.get_by_role('switch',name='사진 올리기 허용')
    check(sw.get_attribute('aria-checked')=='false','처음엔 꺼짐')
    # 켜기: 그 자리에서
    sw.focus(); pg.keyboard.press('Space')
    check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true','누르는 즉시 켜짐으로 보임')
    live(pg,'올릴 수 있어요')
    check(pg.evaluate('window.__same')==1 and pg.url==url,'페이지 이동 없이, 주소 그대로')
    check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true' and pg.locator('.sp-p__tag, .sp-toast').count()>=1,'서버 응답 뒤에도 켜짐, 토스트')
    check(pg.evaluate("document.activeElement.getAttribute('role')")=='switch','초점은 스위치에 그대로')
    pg.wait_for_timeout(500); tb=pg.locator('.sp-toast').bounding_box(); nb=pg.locator('.sp-p__tabs').bounding_box()
    check(abs(nb['y']-(tb['y']+tb['height'])-12)<=1,'토스트는 탭바 위 12px')
    pg.screenshot(path=O+'on.png')
    pg.reload(); check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true' and pg.locator('.sp-toast').count()==0,'새로 고침: 켜짐 그대로, 토스트 없음')
    pg.evaluate('window.__same=1')
    # 빠르게 두 번: 마지막 상태(꺼짐)로
    s2=pg.get_by_role('switch',name='사진 올리기 허용'); s2.click(); s2.click()
    pg.wait_for_function("!document.querySelector('.sp-p[aria-busy]') && (document.getElementById('mem-live').textContent||'').length>0")
    pg.reload(); check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true','빠르게 두 번 누르면 원래대로(켜짐)')
    pg.evaluate('window.__same=1')
    # 실패: 오류 토스트, 스위치 되돌림
    pg.route('**/member/**',lambda r: r.abort() if r.request.method=='POST' else r.continue_())
    pg.get_by_role('switch',name='사진 올리기 허용').click(); pg.wait_for_selector('.sp-toast--error'); pg.wait_for_timeout(200)
    check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true' and '처리하지 못했어요' in pg.evaluate("document.getElementById('mem-urgent').textContent"),'실패하면 스위치 되돌리고 오류 토스트')
    s3=pg.get_by_role('switch',name='사진 올리기 허용'); s3.click(); s3.click(); pg.wait_for_function("!document.querySelector('.sp-p[aria-busy]')"); pg.wait_for_timeout(200)
    check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true','두 번 다 실패해도 서버 상태(켜짐)로')
    pg.unroute('**/member/**')
    # 앞 요청은 성공(그리기 건너뜀), 뒤 요청만 실패 → 서버 상태(앞 요청 결과)로
    n=[0]
    def flaky(r):
        if r.request.method!='POST': return r.continue_()
        n[0]+=1
        return r.continue_() if n[0]==1 else r.abort()
    pg.route('**/member/**',flaky)
    s4=pg.get_by_role('switch',name='사진 올리기 허용'); s4.click(); s4.click(); pg.wait_for_function("!document.querySelector('.sp-p[aria-busy]')"); pg.wait_for_timeout(200)
    shown=pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')
    pg.unroute('**/member/**'); pg.reload(); pg.evaluate('window.__same=1')
    check(shown==pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='false','앞은 성공·뒤는 실패해도 화면=서버(꺼짐)')
    # 내보내기: 이 화면 위 레이어
    pg.get_by_role('button',name='내 가족 아님 · 내보내기 서아 아빠').click(); pg.wait_for_selector('#mem-ask[open]')
    check(pg.evaluate('window.__same')==1 and pg.locator('#mem-ask-t').inner_text()=='서아 아빠 내보낼까요?','내보내기 확인 레이어(이 화면 그대로)')
    check(pg.evaluate("document.activeElement.textContent")=='취소','초점은 취소')
    pg.wait_for_timeout(600); pg.screenshot(path=O+'remove.png')
    pg.keyboard.press('Escape'); check(pg.locator('#mem-ask[open]').count()==0,'Esc로 닫힘')
    pg.get_by_role('button',name='내 가족 아님 · 내보내기 서아 아빠').click(); pg.mouse.click(10,10); check(pg.locator('#mem-ask[open]').count()==0,'바깥 누르면 닫힘')
    pg.get_by_role('button',name='내 가족 아님 · 내보내기 서아 아빠').click(); pg.locator('#mem-ask').get_by_role('button',name='내보내기').click(); pg.wait_for_url('**/settings/family')
    check('처리했어요' in pg.locator('.sp-toast').inner_text() and pg.get_by_role('link',name='서아 아빠').count()==0,'내보내면 설정 > 가족으로, 토스트, 목록에서 빠짐')
    # 스크립트 없이
    y=b.new_context().new_page(); y.goto(B+'/i/'+code); y.fill('#who-name','이모'); y.get_by_role('button',name='들어가기').click(); y.wait_for_url('**/password**'); y.fill('#pw','0917'); y.get_by_role('button',name='들어가기').click(); y.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 이모').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    q=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=c.storage_state()).new_page()
    q.goto(B+'/settings/family'); q.get_by_role('link',name='이모').click(); q.wait_for_url('**/member/**'); q.wait_for_timeout(600)
    q.get_by_role('switch',name='사진 올리기 허용').click(); q.wait_for_url('**done=upload-on**'); q.wait_for_timeout(600)
    check('올릴 수 있어요' in q.locator('.sp-toast').inner_text(),'스크립트 없어도 스위치·토스트')
    q.get_by_role('button',name='내 가족 아님 · 내보내기 이모').click(); q.wait_for_url('**confirm=**')
    check(q.locator('#confirm .sp-layer__title').inner_text()=='이모 내보낼까요?','스크립트 없으면 설정 > 가족 확인 레이어')
    b.close()
print('FAILS',FAILS)
