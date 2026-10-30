# 바로 저장 그 자리에서(76): 설정 첫 화면 스위치·글자 크기·아이(접종 보기)·그룹(이름·기본 포함)이 페이지 이동 없이 + 토스트 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; O=os.path.dirname(os.path.abspath(__file__))+'/../shots/as-'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
def said(pg,word,region='as-live'): pg.wait_for_function("document.getElementById(%r)?.textContent.includes(%r)"%(region,word))
def same(pg): pg.evaluate('window.__same=1')
def still(pg): return pg.evaluate('window.__same')==1
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    # 설정 첫 화면: 가족도 사진 저장하기 스위치
    pg.goto(B+'/settings'); same(pg)
    sw=pg.get_by_role('switch',name='가족도 사진 저장하기'); was=sw.get_attribute('aria-checked'); sw.focus(); pg.keyboard.press('Space')
    said(pg,'저장 버튼이 보여요' if was=='false' else '껐어요')
    check(still(pg) and pg.url.endswith('/settings'),'설정 스위치: 페이지 이동 없이')
    check(pg.get_by_role('switch',name='가족도 사진 저장하기').get_attribute('aria-checked')!=was,'스위치 바뀜')
    check(pg.evaluate("document.activeElement.getAttribute('role')")=='switch','초점은 스위치에 그대로')
    pg.wait_for_timeout(500); tb=pg.locator('.sp-toast').bounding_box(); nb=pg.locator('.sp-p__tabs').bounding_box()
    check(abs(nb['y']-(tb['y']+tb['height'])-12)<=1,'토스트는 탭바 위 12px')
    pg.screenshot(path=O+'settings.png')
    pg.reload(); check(pg.get_by_role('switch',name='가족도 사진 저장하기').get_attribute('aria-checked')!=was and pg.locator('.sp-toast').count()==0,'새로 고침: 바뀐 값, 토스트 없음')
    # 글자 크기: 고르면 그 자리에서
    pg.goto(B+'/settings/text-size'); same(pg)
    check(pg.get_by_role('button',name='저장').count()==0,'저장 버튼은 숨김(스크립트 있음)')
    pg.get_by_label('모두 크게').check(); said(pg,'저장했어요')
    check(still(pg) and pg.get_by_label('모두 크게').is_checked(),'글자 크기: 그 자리에서')
    check(pg.evaluate("document.activeElement.value")=='large','초점은 고른 칸')
    pg.screenshot(path=O+'textsize.png')
    pg.reload(); check(pg.get_by_label('모두 크게').is_checked(),'새로 고침해도 저장됨')
    # 실패하면 서버 상태로 되돌리고 오류 토스트
    same(pg); pg.route('**/settings/text-size',lambda r: r.abort() if r.request.method=='POST' else r.continue_())
    pg.get_by_label('모두 기본').check(); said(pg,'저장하지 못했어요','as-urgent'); pg.wait_for_function("!document.querySelector('.sp-p[aria-busy]')")
    check(still(pg) and pg.get_by_label('모두 크게').is_checked(),'실패하면 고른 칸을 서버 값으로 되돌림')
    pg.unroute('**/settings/text-size')
    # 아이: 접종·검진 보기 체크
    pg.goto(B+'/settings/children'); same(pg)
    hc=pg.get_by_label('알림 탭에 다가오는 일정 보기'); was=hc.is_checked(); hc.click(); said(pg,'저장했어요')
    check(still(pg) and pg.get_by_label('알림 탭에 다가오는 일정 보기').is_checked()!=was,'아이 접종 보기: 그 자리에서')
    # 그룹: 이름(빈칸이면 오류)·기본 포함
    pg.goto(B+'/settings/family/groups'); pg.locator('a[href^="/settings/family/groups/"]').filter(has_text='가족').first.click(); pg.wait_for_url('**/groups/*'); same(pg)
    pg.fill('#name','   '); pg.press('#name','Enter'); pg.wait_for_selector('#g-err')
    said(pg,'1~12자','as-urgent')
    check(still(pg) and pg.evaluate("document.activeElement.id")=='name' and '1~12자' in pg.evaluate("document.getElementById('as-urgent').textContent"),'그룹 이름 공백만: 그 자리에서 오류, 이름 칸으로 초점')
    pg.fill('#name','외가'); pg.press('#name','Enter'); said(pg,'저장했어요')
    check(still(pg) and pg.locator('.sp-p__nav-title').inner_text()=='외가' and pg.locator('#g-err').count()==0,'그룹 이름 저장: 제목도 바뀜, 오류 사라짐')
    inc=pg.get_by_label('새 사진에 기본으로 포함'); was=inc.is_checked(); inc.click(); said(pg,'저장했어요')
    check(still(pg) and pg.get_by_label('새 사진에 기본으로 포함').is_checked()!=was and pg.locator('#name').input_value()=='외가','기본 포함(폼 밖 칸): 그 자리에서, 이름 그대로')
    pg.screenshot(path=O+'group.png')
    # Enter는 한 번만 보냄
    n=[]; pg.on('request',lambda r: n.append(1) if r.method=='POST' else None)
    pg.fill('#name','외가2'); pg.press('#name','Enter'); said(pg,'저장했어요'); pg.wait_for_timeout(500)
    check(len(n)==1,'이름 칸 Enter: 한 번만 보냄 (%d)'%len(n))
    # 응답 기다리는 동안 이어서 쓰던 글은 남음
    pg.route('**/groups/*',lambda r: (pg.wait_for_timeout(0), r.continue_()) and None if r.request.method!='POST' else (__import__('time').sleep(0.8), r.continue_()))
    pg.fill('#name','외가3'); pg.keyboard.press('Tab'); pg.focus('#name'); pg.keyboard.press('End'); pg.keyboard.type('집')
    said(pg,'저장했어요'); pg.wait_for_timeout(200)
    check(pg.locator('#name').input_value()=='외가3집' and pg.evaluate("document.activeElement.id")=='name','응답 와도 이어서 쓰던 글·커서 그대로')
    pg.unroute('**/groups/*')
    # 스크립트 없이: 저장 버튼으로
    q=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=c.storage_state()).new_page()
    q.goto(B+'/settings/text-size'); q.get_by_label('모두 기본').check(); q.get_by_role('button',name='저장').click(); q.wait_for_url('**done=saved**')
    check('저장했어요' in q.locator('.sp-toast').inner_text(),'스크립트 없으면 저장 버튼 → 토스트')
    b.close()
print('FAILS',FAILS)
