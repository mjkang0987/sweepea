import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m, flush=True); c or fails.append(m)
def up(pg,f):
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    up(pg,'u0.jpg'); up(pg,'u1.jpg'); up(pg,'u2.jpg')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gc=b.new_context(viewport={'width':390,'height':844},accept_downloads=True); gp=gc.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+'/album?v=list')
    check(gp.get_by_role('link',name='골라서 저장하기').count()==0,'저장 꺼져 있으면 버튼 없음')
    gp.goto(B+'/album/save'); check('v=list' in gp.url,'저장 꺼져 있으면 고르기 화면 대신 모아 보기로')
    pg.goto(B+'/settings'); sw=pg.get_by_role('switch',name='가족도 사진 저장하기'); sw.click(); pg.wait_for_function("document.querySelector('[role=switch]').getAttribute('aria-checked')==='true'")  # 그 자리에서 저장(주소 안 바뀜)
    gp.goto(B+'/album?v=list'); gp.get_by_role('link',name='골라서 저장하기').click(); gp.wait_for_url('**/album/save**')
    st=gp.locator('[data-count]')
    check(gp.locator('.sp-s__check').count()==3,'사진 3장 고를 수 있음')
    check(gp.get_by_role('button',name='휴대폰에 저장하기').is_disabled(),'안 골랐을 땐 버튼 꺼짐')
    labels=gp.locator('.sp-s__pick')
    labels.nth(0).click(); labels.nth(2).click()
    check(st.inner_text().startswith('2장 골랐어요'),'2장 골랐어요 표시')
    check(gp.get_by_role('button',name='2장 휴대폰에 저장하기').count()==1,'버튼에 장수')
    check(gp.locator('.sp-s__check').nth(0).is_checked(),'체크박스로 골라짐')
    gp.screenshot(path=S+'save-pick.png')
    labels.nth(2).click(); check(st.inner_text().startswith('1장'),'한 번 더 누르면 빠짐'); labels.nth(2).click()
    names=[]
    gp.on('download', lambda d: names.append(d.suggested_filename))
    gp.get_by_role('button',name='2장 휴대폰에 저장하기').click()
    gp.wait_for_function("document.querySelector('[data-count]').textContent.includes('저장했어요')",timeout=20000)
    gp.wait_for_timeout(1500)
    check(len(names)==2 and all(n.startswith('sweepea-') and n.endswith('.jpg') for n in names),'PC는 한 장씩 2개 내려받음 '+str(names))
    # 큰 글씨(아주 크게) 화면
    big=b.new_context(viewport={'width':390,'height':844}); 
    big.add_cookies(gc.cookies()); bp=big.new_page()
    # 스크립트 없이
    nj=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nj.add_cookies(gc.cookies()); np_=nj.new_page()
    np_.goto(B+'/album/save'); np_.locator('.sp-s__pick').nth(0).click(); np_.locator('.sp-s__pick').nth(1).click()
    np_.get_by_role('button',name='휴대폰에 저장하기').click(); np_.wait_for_load_state()
    lk=np_.get_by_role('link',name='저장')
    check(lk.count()==2 and all(lk.nth(i).get_attribute('download') for i in range(2)),'스크립트 없이: 고른 사진마다 저장 링크')
    np_.screenshot(path=S+'save-nojs.png')
print('FAILS',fails)
