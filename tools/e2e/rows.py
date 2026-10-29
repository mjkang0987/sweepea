# 묶음 안 줄 + 고르면 바로 적용(글자 크기·아이·그룹 상세), 스크립트 없으면 저장 버튼
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; S='/home/claude/sweepea/tools/shots/rows/'
import os; os.makedirs(S,exist_ok=True)
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/children/new'); pg.fill('#name','도윤'); pg.fill('#birth','2026-08-30'); pg.get_by_role('button',name='추가').click(); pg.wait_for_url('**done=added**')
    # 글자 크기: 라디오 오른쪽, 누르면 저장
    pg.goto(B+'/settings/text-size'); check(pg.get_by_role('button',name='저장').is_hidden(),'글자 크기: 저장 버튼 숨김')
    r=pg.get_by_label('모두 크게'); rb=r.bounding_box(); check(rb['x']>300,'라디오가 오른쪽')
    pg.screenshot(path=S+'TextSize.png'); r.check(); pg.wait_for_function("document.getElementById('as-live')?.textContent.trim().length>0"); check(pg.get_by_label('모두 크게').is_checked(),'고르면 바로 저장')
    # 아이
    pg.goto(B+'/settings/children'); check(pg.get_by_role('link',name='변경 (하린)').count()==1,'아이 줄 변경')
    a=pg.get_by_role('link',name='아이 추가'); check(a.evaluate("e=>getComputedStyle(e).color")!='rgb(29, 29, 31)','아이 추가 초록')
    pg.screenshot(path=S+'ChildSettings.png'); c=pg.get_by_label('앨범에 접종·검진 일정 보기'); was=c.is_checked(); c.click(); pg.wait_for_function("document.getElementById('as-live')?.textContent.trim().length>0"); check(pg.get_by_label('앨범에 접종·검진 일정 보기').is_checked()!=was,'접종 보기 바로 저장')
    # 그룹 상세
    pg.goto(B+'/settings/family/groups'); g=pg.locator('a[href^="/settings/family/groups/"]:not([href$="new"])').first.get_attribute('href'); pg.goto(B+g)
    pg.screenshot(path=S+'GroupDetail.png')
    inc=pg.get_by_label('새 사진에 기본으로 포함'); was=inc.is_checked(); inc.click(); pg.wait_for_function("document.getElementById('as-live')?.textContent.trim().length>0"); check(pg.get_by_label('새 사진에 기본으로 포함').is_checked()!=was,'기본 포함 바로 저장')
    pg.fill('#name','외가'); pg.press('#name','Enter'); pg.wait_for_function("document.getElementById('as-live')?.textContent.trim().length>0"); check(pg.locator('.sp-p__nav-title').inner_text()=='외가','이름 바꾸고 Enter → 저장')
    check(pg.get_by_role('button',name='외가 주소 카톡으로 보내기 새로 들어오는 사람은 보낸 뒤 3일 안에').count()==1,'주소 보내기 줄')
    # 스크립트 없이
    nj=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nj.add_cookies(ctx.cookies()); q=nj.new_page()
    q.goto(B+'/settings/text-size'); check(q.get_by_role('button',name='저장').is_visible(),'스크립트 없음: 저장 버튼 보임')
    q.get_by_label('모두 기본').check(); q.get_by_role('button',name='저장').click(); q.wait_for_url('**done=saved**'); check(True,'스크립트 없음: 저장 버튼으로')
print('FAILS',fails)
