# 사진 정보 수정 저장 그 자리에서(73): 스크립트 있으면 이 화면 그대로 '저장했어요.' 토스트, 없으면 크게 보기로 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'; O=D+'../shots/ps-'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
SAVED="document.getElementById('ph-live')?.textContent.includes('저장했어요')"
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    url=pg.url; pg.evaluate('window.__same=1')
    # 저장: 그 자리에서
    pg.fill('#date','2026-02-03'); save=pg.get_by_role('button',name='저장'); save.focus(); pg.keyboard.press('Enter')
    pg.wait_for_function(SAVED)
    check(pg.evaluate('window.__same')==1 and pg.url==url,'저장은 페이지 이동 없이, 주소 그대로')
    t=pg.locator('.sp-toast'); check(t.count()==1 and t.inner_text()=='저장했어요.' and t.get_attribute('role') is None,'저장했어요 토스트(읽기는 알림 칸)')
    check(pg.evaluate("document.activeElement.value")=='save','초점은 저장 버튼에 그대로')
    pg.wait_for_timeout(500); tb=t.bounding_box(); nb=pg.locator('.sp-p__tabs').bounding_box()
    check(abs(nb['y']-(tb['y']+tb['height'])-12)<=1,'토스트는 탭바 위 12px')
    pg.screenshot(path=O+'saved.png')
    pg.reload(); check(pg.locator('#date').input_value()=='2026-02-03' and pg.locator('.sp-toast').count()==0,'새로 고침하면 저장한 값, 토스트 없음')
    pg.evaluate('window.__same=1')
    # 두 번 눌러도 한 번만 보냄
    n=[]; pg.on('request',lambda r: n.append(1) if r.method=='POST' else None)
    pg.evaluate("document.querySelector('.sp-p__form button[value=save]').click(); document.querySelector('.sp-p__form button[value=save]').click()")
    pg.wait_for_function(SAVED); pg.wait_for_timeout(300)
    check(len(n)==1,'두 번 눌러도 한 번 보냄 (%d)'%len(n))
    # 실패: 오류 토스트, 다시 누를 수 있음
    pg.route('**/photo/**',lambda r: r.abort() if r.request.method=='POST' else r.continue_())
    pg.get_by_role('button',name='저장').click(); pg.wait_for_selector('.sp-toast--error'); pg.wait_for_timeout(200)
    check('저장하지 못했어요' in pg.evaluate("document.getElementById('ph-urgent').textContent") and pg.get_by_role('button',name='저장').is_enabled(),'실패하면 오류 토스트·다시 누를 수 있음')
    pg.unroute('**/photo/**')
    # 고칠 게 있으면 폼만 바뀌고, 고친 뒤 저장하면 안내가 사라짐
    pg.get_by_label('가족',exact=True).uncheck(); pg.get_by_role('button',name='저장').click(); pg.wait_for_selector('#p-err')
    check(pg.evaluate('window.__same')==1 and pg.evaluate("document.activeElement.name")=='group','그룹 없으면 폼만 바뀌고 그룹 칸으로 초점')
    pg.get_by_label('가족',exact=True).check(); pg.get_by_role('button',name='저장').click(); pg.wait_for_function(SAVED)
    check(pg.locator('#p-err').count()==0 and pg.locator('[aria-invalid]').count()==0 and pg.locator('[aria-describedby~="p-err"]').count()==0,'고쳐서 저장하면 오류 안내 지워짐')
    # 스크립트 없이: 예전처럼 크게 보기로
    q=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=c.storage_state()).new_page()
    q.goto(url); q.get_by_role('button',name='저장').click(); q.wait_for_url('**/view/**done=saved**')
    check('저장했어요' in q.locator('.sp-toast').inner_text(),'스크립트 없으면 크게 보기로 돌아와 안내')
    b.close()
print('FAILS',FAILS)
