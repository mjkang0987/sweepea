# 그룹 관리: 목록·추가·상세(이름·기본 포함)·비밀번호 바꾸기·주소 다시 만들기
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    def shot(n): pg.screenshot(path=D+'g-'+n+'.png',full_page=True)
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('link',name='그룹 관리').click(); pg.wait_for_url('**/groups')
    check(pg.locator('.sp-p__row',has_text='가족').count()==1,'그룹 목록'); 
    pg.get_by_role('link',name='그룹 추가').click(); pg.wait_for_url('**/groups/new')
    pg.fill('#name','친가'); pg.fill('#pw','1234'); pg.fill('#hint','1234 생일'); pg.get_by_role('button',name='추가').click()
    check('힌트에 비밀번호' in pg.get_by_role('alert').inner_text(),'힌트에 비밀번호 쓰면 오류')
    pg.fill('#pw','5678'); pg.fill('#hint','할아버지 생신'); pg.get_by_label('새 사진에 기본으로 포함').uncheck(); pg.get_by_role('button',name='추가').click(); pg.wait_for_url('**done=added**')
    check(pg.locator('.sp-p__row',has_text='친가').locator('.sp-p__tag').count()==0,'기본 포함 끈 그룹은 표시 없음'); shot('1')
    pg.goto(B+'/settings/family/groups/new'); pg.fill('#name','친가'); pg.fill('#pw','1111'); pg.get_by_role('button',name='추가').click()
    check('같은 이름' in pg.get_by_role('alert').inner_text(),'같은 이름 그룹은 오류')
    pg.goto(B+'/upload'); check(not pg.get_by_label('친가').is_checked() and pg.get_by_label('가족',exact=True).is_checked(),'올리기 화면 기본 체크가 설정대로')
    # 상세
    pg.goto(B+'/settings/family/groups'); pg.locator('.sp-p__row',has_text='친가').click(); pg.wait_for_url('**/groups/*')
    check('힌트 · 할아버지 생신' in pg.content(),'상세에 힌트'); 
    pg.fill('#name','할머니댁'); pg.press('#name','Enter'); pg.wait_for_url('**done=saved**'); pg.get_by_label('새 사진에 기본으로 포함').check(); pg.wait_for_url('**done=saved**')
    check(pg.get_by_role('heading',name='할머니댁').count()==1 and pg.get_by_label('새 사진에 기본으로 포함').is_checked(),'이름·기본 포함 저장'); shot('2')
    gid=pg.url.split('/groups/')[1].split('?')[0]
    # 링크 → 가족 입장 → 상세 구성원
    pg.get_by_role('button',name='할머니댁 주소 카톡으로 보내기').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','5678'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family/groups/'+gid); check('확인 기다림 · 3일 남음' in pg.content(),'승인 대기 구성원 남은 날')
    # 비밀번호 바꾸기
    pg.locator('a[href$="/password"]').click(); pg.wait_for_url('**/password')
    pg.fill('#pw','4321'); pg.fill('#hint','새 힌트'); pg.get_by_role('button',name='저장').click(); pg.wait_for_url('**done=password**')
    check('힌트 · 새 힌트' in pg.content(),'비밀번호·힌트 바꿈'); shot('3')
    n=b.new_context(viewport={'width':390,'height':844}); np=n.new_page(); np.goto(B+'/i/'+code)
    np.fill('#who-name','고모'); np.get_by_role('button',name='들어가기').click(); np.wait_for_url('**/password**'); np.fill('#pw','5678'); np.get_by_role('button',name='들어가기').click()
    check('맞지 않아요' in np.content(),'예전 비밀번호는 안 됨')
    np.fill('#pw','4321'); np.get_by_role('button',name='들어가기').click(); np.wait_for_url('**/wait'); check(True,'새 비밀번호로 들어감')
    # 주소 다시 만들기
    pg.goto(B+'/settings/family/groups/'+gid); pg.get_by_role('button',name='주소 다시 만들기 (예전 주소는 바로 막혀요)').click(); pg.wait_for_url('**confirm=reset**')
    check('할머니댁 주소를 다시 만들까요?' in pg.content(),'다시 만들기 확인'); shot('4')
    pg.locator('#confirm').get_by_role('button',name='다시 만들기').click(); pg.wait_for_url('**#link')
    code2=pg.locator('#link-url').input_value().rsplit('/',1)[1]; check(code2!=code,'새 주소')
    x=b.new_context().new_page(); x.goto(B+'/i/'+code); check('/i/' in x.url and ('없' in x.content() or '찾을 수' in x.content()),'예전 주소는 막힘')
    x.goto(B+'/i/'+code2); check(x.locator('#who-name').count()==1,'새 주소는 열림')
    b.close()
print('ALL OK')
