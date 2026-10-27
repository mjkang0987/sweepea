# 저장 버튼 아래 고정 + 접종 바로 저장(78): 막대는 탭바 바로 위, 끝까지 내리면 내용이 막대에 안 가림, 토스트는 막대 위 12px.
# 접종은 체크하면 그 자리에서 저장되고 완료로 옮겨감 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'; O=D+'../shots/sb-'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
def bar_ok(pg,name):
    bar=pg.locator('.sp-p__savebar').bounding_box(); tabs=pg.locator('.sp-p__tabs').bounding_box()
    check(abs((bar['y']+bar['height'])-tabs['y'])<=1,name+': 막대는 탭바 바로 위')
    pg.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)'); pg.wait_for_timeout(200)
    last=pg.evaluate("(()=>{const els=[...document.querySelectorAll('.sp-p > *:not(.sp-vh):not(dialog):not(.sp-toast)')].filter(e=>!e.closest('.sp-p__savebar')&&e.getBoundingClientRect().height>0);return Math.max(...els.map(e=>e.getBoundingClientRect().bottom))})()")
    check(last<=pg.locator('.sp-p__savebar').bounding_box()['y']+1,name+': 끝까지 내리면 내용이 막대에 안 가림 (%d)'%last)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    # 아이 추가·그룹 추가·비밀번호
    pg.goto(B+'/settings/children/new'); bar_ok(pg,'아이 추가'); pg.screenshot(path=O+'child.png')
    pg.fill('#name','도윤'); pg.fill('#birth','2026-08-30'); pg.locator('.sp-p__savebar').get_by_role('button',name='추가').click(); pg.wait_for_url('**/settings/children**')
    check(True,'막대 버튼으로 추가됨')
    pg.goto(B+'/settings/family/groups/new'); bar_ok(pg,'그룹 추가')
    pg.goto(B+'/settings/family/groups'); pg.locator('a[href^="/settings/family/groups/"]').filter(has_text='가족').first.click(); pg.wait_for_url('**/groups/*')
    pg.goto(pg.url+'/password'); bar_ok(pg,'비밀번호')
    # 사진 정보 수정: 막대 + 저장 토스트는 막대 위 12px
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    bar_ok(pg,'사진 정보 수정')
    pg.locator('.sp-p__savebar').get_by_role('button',name='저장').click(); pg.wait_for_function("document.getElementById('ph-live')?.textContent.includes('저장했어요')"); pg.wait_for_timeout(500)
    t=pg.locator('.sp-toast').bounding_box(); bb=pg.locator('.sp-p__savebar').bounding_box()
    check(abs(bb['y']-(t['y']+t['height'])-12)<=1,'사진 저장 토스트는 막대 위 12px')
    pg.screenshot(path=O+'photo.png')
    # 접종: 체크하면 바로 저장
    pg.goto(B+'/home'); href=pg.locator('a[href^="/health/"]').first.get_attribute('href'); pg.goto(B+href); pg.evaluate('window.__same=1')
    check(pg.get_by_role('button',name='저장').count()==0,'접종: 저장 버튼 숨김(바로 저장)')
    past=pg.locator('details#past')
    if past.count(): past.locator('summary').click()
    box=pg.locator('#sec-next ~ ul input[name=done]').first if pg.locator('#sec-next ~ ul input[name=done]').count() else pg.locator('details#past input[name=done]').first
    name=box.evaluate("e=>e.closest('label').querySelector('.sp-p__who-name').textContent")
    box.check(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    check(pg.evaluate('window.__same')==1,'접종 체크: 페이지 이동 없이')
    done_names=pg.locator('#sec-done ~ ul .sp-p__who-name').all_inner_texts()
    check(name in done_names,'체크한 일정이 완료로 옮겨감 (%s)'%name)
    check(pg.evaluate("document.activeElement.checked===true && !!document.activeElement.closest('#sec-done ~ ul, section')"),'초점은 옮겨간 칸')
    if past.count(): check(pg.locator('details#past[open]').count()==1 or pg.locator('details#past').count()==0,'펼쳐 둔 지난 일정은 그대로 펼침')
    pg.wait_for_timeout(500); pg.screenshot(path=O+'health.png')
    pg.reload(); check(name in pg.locator('#sec-done ~ ul .sp-p__who-name').all_inner_texts(),'새로 고침해도 완료')
    # 완료에서 풀기
    pg.evaluate('window.__same=1')
    pg.locator('#sec-done ~ ul label', has_text=name).locator('input[name=done]').uncheck(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    check(pg.evaluate('window.__same')==1 and name not in pg.locator('#sec-done ~ ul .sp-p__who-name').all_inner_texts(),'완료에서 풀면 그 자리에서 빠짐')
    # 스크립트 없이: 저장 버튼
    q=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=c.storage_state()).new_page()
    q.goto(B+href); check(q.get_by_role('button',name='저장').is_visible(),'스크립트 없으면 접종 저장 버튼')
    b.close()
print('FAILS',FAILS)
