from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def start(b,birth,scheme='light'):
    pg=b.new_context(viewport={'width':390,'height':844},color_scheme=scheme).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth',birth); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    return pg
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=start(b,'2026-07-19')
    d=pg.get_by_role('dialog')
    check(d.count()==1 and '태어난 지 100일이에요' in d.inner_text() and '오늘은 하린이' in d.inner_text(),'백일 레이어')
    check(pg.evaluate("document.activeElement.textContent.trim()")=='사진 올리기','첫 버튼에 초점')
    pg.screenshot(path=D+'ly4-100.png')
    d.get_by_role('button',name='닫기').click(); pg.wait_for_url('**/home')
    d=pg.get_by_role('dialog')
    check(d.count()==1 and '저장 공간이 거의 찼어요' in d.inner_text(),'백일 닫은 뒤 저장 공간 레이어')
    check(pg.locator('.sp-layer meter').get_attribute('value') in ('90','91','92','93'),'막대 값')
    pg.screenshot(path=D+'ly5-storage.png')
    d.get_by_role('button',name='저장 용량 보기').click(); pg.wait_for_url('**/settings/storage')
    pg.goto(B+'/home'); check(pg.get_by_role('dialog').count()==0,'둘 다 닫은 뒤 레이어 없음')
    pg.reload(); check(pg.get_by_role('dialog').count()==0,'다시 열어도 없음')
    # 돌 + 사진 올리기, 다크
    pg2=start(b,'2025-10-26','dark')
    d=pg2.get_by_role('dialog'); check('첫 생일이에요' in d.inner_text(),'돌 레이어')
    pg2.screenshot(path=D+'ly4-dol-dark.png')
    d.get_by_role('button',name='사진 올리기').click(); pg2.wait_for_url('**/upload')
    pg2.goto(B+'/home'); check('생일' not in (pg2.get_by_role('dialog').inner_text() if pg2.get_by_role('dialog').count() else ''),'올리기 뒤 생일 레이어 없음')
    # 평범한 날
    pg3=start(b,'2025-10-25'); txt=pg3.get_by_role('dialog').inner_text() if pg3.get_by_role('dialog').count() else ''
    check('생일' not in txt and '100일' not in txt,'평범한 날은 생일 레이어 없음')
print('FAILS',fails)
