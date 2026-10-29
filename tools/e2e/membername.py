# 구성원 이름 바꾸기(사용자 2026-10-29 "이름 바꿀 수 있게 해줘, 접속한 사람"): 설정 › 가족 › 그 사람에서 '부르는 이름' 바꾸기,
# 같은 그룹 같은 이름은 막고, 1~12자. 바꾸면 가족 목록에도 새 이름 (mock, 인자: 스크린샷 폴더 엔진)
import sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    pg=br.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    for who in ('할미','외할아버지'):
        g=br.new_context(viewport={'width':390,'height':844}).new_page(); g.goto(B+'/i/'+code)
        g.fill('#who-name',who); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/password**'); g.fill('#pw','0917'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/wait')
        pg.goto(B+'/settings/family'); pg.get_by_role('button',name=f'승인 {who}').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    pg.goto(B+'/settings/family'); pg.get_by_role('link',name='할미').first.click(); pg.wait_for_url('**/member/**')
    inp=pg.get_by_label('부르는 이름'); check(inp.input_value()=='할미','이름 칸에 지금 이름')
    inp.fill('  외할머니  '); pg.get_by_role('button',name='이름 바꾸기').click(); pg.wait_for_url('**done=renamed**')
    check(pg.locator('.sp-toast').is_visible() and '이름을 바꿨어요' in pg.locator('.sp-toast').inner_text(),'바꾸면 토스트')
    check(pg.get_by_role('heading',level=1).inner_text()=='외할머니','제목도 새 이름(앞뒤 공백 뺌)')
    pg.screenshot(path=W+'/mn-renamed.png')
    pg.get_by_label('부르는 이름').fill('외할아버지'); pg.get_by_role('button',name='이름 바꾸기').click(); pg.wait_for_url('**done=name-taken**')
    check('예전에 쓴 이름' in pg.locator('.sp-toast').inner_text() and pg.locator('#m-name-err').is_visible() and pg.get_by_label('부르는 이름').get_attribute('aria-invalid')=='true','같은 그룹 같은 이름은 막음')
    pg.goto(B+'/settings/family'); t=pg.locator('main').inner_text()
    check('외할머니' in t and '할미' not in t,'가족 목록에도 새 이름')
    br.close()
print('FAILS',fails)
