# 부모 사진 정보: 그룹 빼기 → 그 가족 앨범에서 사라짐, 찍은 날 바꾸기, 아이 태그, 지우기
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    def shot(n): pg.screenshot(path=D+'ph-'+n+'.png',full_page=True)
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/children/new'); pg.fill('#name','도윤'); pg.fill('#birth','2026-08-30'); pg.get_by_role('button',name='추가').click(); pg.wait_for_url('**done=added**')
    pg.goto(B+'/settings/family/groups/new'); pg.fill('#name','친가'); pg.fill('#pw','5678'); pg.get_by_label('새 사진에 기본으로 포함').uncheck(); pg.get_by_role('button',name='추가').click(); pg.wait_for_url('**done=added**')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 이모').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+'/album'); check(gp.locator('.sp-a__card-link').count()==1,'가족 앨범에 1장')
    # 사진 정보
    pg.goto(B+'/home'); pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    check(pg.get_by_label('가족',exact=True).is_checked() and not pg.get_by_label('친가').is_checked(),'처음엔 기본 포함 그룹에만 보임'); shot('1')
    pg.get_by_label('가족',exact=True).uncheck(); pg.get_by_label('친가').uncheck(); pg.get_by_role('button',name='저장').click(); pg.wait_for_load_state()
    check('하나 이상' in pg.get_by_role('alert').inner_text(),'그룹 하나도 없으면 오류')
    pg.get_by_label('친가').check(); pg.get_by_label('도윤').check(); pg.fill('#date','2026-01-02'); pg.get_by_role('button',name='저장').click(); pg.wait_for_url('**/view/**done=saved**')
    check(pg.locator('.sp-toast').inner_text()=='사진 정보를 저장했어요.','저장하면 크게 보기로 돌아와 안내')
    pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    check(pg.get_by_role('heading',level=1).inner_text()=='사진 정보 수정' and pg.get_by_role('link',name='닫기').get_attribute('href').startswith('/view/'),'수정 화면 제목·닫기')
    check(pg.get_by_label('친가').is_checked() and not pg.get_by_label('가족',exact=True).is_checked() and pg.get_by_label('도윤').is_checked() and pg.locator('#date').input_value()=='2026-01-02','저장한 값')
    gp.goto(B+'/album'); check(gp.locator('.sp-a__card-link').count()==0,'그룹을 빼면 그 가족 앨범에서 사라짐')
    pg.goto(B+'/home'); check(pg.get_by_role('heading',name='1월',exact=True).count()==1,'찍은 날 바꾸면 앨범 달이 바뀜(올해는 "1월")')
    # 지우기
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    pg.get_by_role('link',name='사진 지우기').click(); pg.wait_for_selector('#confirm'); shot('2')
    pg.locator('#confirm').get_by_role('button',name='지우기').click(); pg.wait_for_url('**done=deleted*')
    check(pg.locator('.sp-p__cell-link').count()==0 and '지웠어요' in pg.content(),'지우면 앨범에서 빠짐')
    pg.goto(B+'/settings/storage'); check('0MB' in pg.content() and '사진 0장' in pg.content(),'지우면 용량·사진 수에서 빠짐')
    pg.goto(B+'/photo/00000000-0000-4000-8000-000000000999'); check(pg.url.endswith('/home'),'없는 사진은 앨범으로')
    b.close()
print('ALL OK')
