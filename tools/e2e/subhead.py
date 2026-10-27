# 하위 화면 머리글: 왼쪽 ‹ 이전, 가운데 작은 제목(디자인). 자리 재기 + 캡처
import layerfix, re
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/sub/'
import os; os.makedirs(S,exist_ok=True)
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_url('**done=member-active**')
    member=pg.locator('a[href^="/settings/family/member/"]').first.get_attribute('href')
    pg.goto(B+'/settings/family/groups'); group=pg.locator('a[href^="/settings/family/groups/"]:not([href$="new"])').first.get_attribute('href')
    kid=pg.evaluate("fetch('/home').then(r=>r.text())")
    pg.goto(B+'/home'); health=pg.locator('a[href^="/health/"]').first.get_attribute('href')
    pg.goto(B+'/settings/children'); child=pg.locator('a[href^="/settings/children/"]:not([href$="new"])').first.get_attribute('href')
    pages=[('Family','/settings/family','가족'),('GroupSettings','/settings/family/groups','그룹'),('GroupAdd','/settings/family/groups/new','그룹 추가'),('GroupDetail',group,None),('PasswordChange',group+'/password','비밀번호 바꾸기'),('MemberDetail',member,'외할머니'),('SendSetup','/settings/family/sms','문자로 공유하기'),('TextSize','/settings/text-size','가족 화면 글자 크기'),('ChildSettings','/settings/children','아이'),('ChildAdd','/settings/children/new',None),('ChildEdit',child,None),('Storage','/settings/storage','저장 용량'),('Account','/settings/account','계정'),('Health',health,'접종·검진')]
    for name,path,title in pages:
        pg.goto(B+path)
        h=pg.locator('.sp-p__nav-title'); bk=pg.locator('.sp-p__nav .sp-p__back')
        hb=h.bounding_box(); bb=bk.bounding_box()
        cy=lambda r: r['y']+r['height']/2
        ok=abs((hb['x']+hb['width']/2)-195)<=1 and abs(cy(hb)-cy(bb))<=1 and abs(cy(bb)-46)<=1 and bb['x']==20
        check(ok and pg.locator('h1').count()==1 and (title is None or h.inner_text()==title),f'{name} 제목 "{h.inner_text()}" 가운데·뒤로와 한 줄')
        pg.screenshot(path=S+name+'.png')
print('FAILS',fails)
