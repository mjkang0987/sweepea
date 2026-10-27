# 그룹 상세 그 자리에서(77): 주소 보내기 → 이 화면에 링크 카드, 주소 다시 만들기 → 확인 레이어 → 이 화면에 새 링크 카드 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; O=os.path.dirname(os.path.abspath(__file__))+'/../shots/gp-'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family/groups'); pg.locator('a[href^="/settings/family/groups/"]').filter(has_text='가족').first.click(); pg.wait_for_url('**/groups/*')
    url=pg.url; pg.evaluate('window.__same=1')
    # 주소 보내기: 이 화면에 링크 카드
    pg.get_by_role('button',name='가족 주소 카톡으로 보내기').click(); pg.wait_for_selector('#link-url')
    check(pg.evaluate('window.__same')==1 and pg.url==url,'주소 보내기: 페이지 이동 없이')
    check(pg.evaluate("document.activeElement.id")=='link-title','링크 카드 제목으로 초점')
    check(pg.evaluate("document.querySelector('.sp-p__rows').nextElementSibling.id")=='link','카드는 목록 바로 아래')
    first=pg.locator('#link-url').input_value()
    pg.wait_for_timeout(300); pg.screenshot(path=O+'card.png')
    # 이름을 저장해 화면이 갈려도 카드는 남음
    pg.fill('#name','외가'); pg.press('#name','Enter'); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    check(pg.locator('#link-url').input_value()==first and pg.locator('#link').count()==1,'이름 저장 뒤에도 링크 카드 그대로')
    # 이름 저장 응답을 기다리는 동안 연 확인 레이어는 그대로
    import time
    pg.route('**/groups/*',lambda r: (time.sleep(0.8), r.continue_()) if r.request.method=='POST' else r.continue_())
    pg.fill('#name','외가집'); pg.get_by_role('button',name='주소 다시 만들기 (예전 주소는 바로 막혀요)').click(); pg.wait_for_selector('#grp-ask[open]')
    pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')"); pg.wait_for_timeout(200)
    check(pg.locator('#grp-ask[open]').count()==1 and pg.evaluate("!!document.activeElement.closest('#grp-ask')"),'저장 응답이 와도 열린 확인 레이어·초점 그대로')
    pg.keyboard.press('Escape'); pg.unroute('**/groups/*')
    pg.fill('#name','외가'); pg.press('#name','Enter'); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    # 다시 만들기: 확인 레이어 → 새 링크
    pg.get_by_role('button',name='주소 다시 만들기 (예전 주소는 바로 막혀요)').click(); pg.wait_for_selector('#grp-ask[open]')
    check(pg.locator('#grp-ask-t').inner_text()=='외가 주소를 다시 만들까요?' and pg.evaluate("document.activeElement.textContent")=='취소','다시 만들기 확인 레이어, 초점은 취소')
    pg.wait_for_timeout(600); pg.screenshot(path=O+'reset.png')
    pg.keyboard.press('Escape'); check(pg.locator('#grp-ask[open]').count()==0 and pg.locator('#link-url').input_value()==first,'Esc로 닫으면 그대로')
    pg.get_by_role('button',name='주소 다시 만들기 (예전 주소는 바로 막혀요)').click(); pg.locator('#grp-ask').get_by_role('button',name='다시 만들기').click()
    pg.wait_for_function("document.getElementById('link-url') && document.getElementById('link-url').value!==%r"%first)
    check(pg.evaluate('window.__same')==1 and pg.locator('#link').count()==1,'다시 만들면 이 화면에 새 링크 카드(하나만)')
    old=b.new_context().new_page(); old.goto(first)
    check('누구세요' not in old.content(),'예전 주소는 막힘')
    new=pg.locator('#link-url').input_value(); n=b.new_context().new_page(); n.goto(new)
    check('누구세요' in n.title() or n.locator('#who-name').count()==1,'새 주소는 열림')
    # 실패: 오류 토스트
    pg.route('**/settings/family',lambda r: r.abort() if r.request.method=='POST' else r.continue_())
    pg.get_by_role('button',name='외가 주소 카톡으로 보내기').click(); pg.wait_for_selector('.sp-toast--error')
    check(pg.locator('#link-url').input_value()==new,'실패하면 오류 토스트, 카드 그대로')
    pg.unroute('**/settings/family')
    # 스크립트 없이: 설정 > 가족으로
    q=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=c.storage_state()).new_page()
    q.goto(url); q.wait_for_timeout(600); q.get_by_role('button',name='외가 주소 카톡으로 보내기').click(); q.wait_for_url('**/settings/family**')
    check(q.locator('#link-url').count()==1,'스크립트 없으면 설정 > 가족에서 링크 카드')
    b.close()
print('FAILS',FAILS)
