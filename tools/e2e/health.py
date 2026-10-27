# 접종·검진: 앨범 위 다음 일정, 체크·저장 → 완료, 다시 풀기, 일정 보기 끄기
from playwright.sync_api import sync_playwright
import datetime
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    row=pg.locator('a[href^="/health/"]'); check(row.count()==1 and '생후 13개월' in row.inner_text() and '다음:' not in row.inner_text(),'앨범 위 다음 일정 ('+row.inner_text().replace('\n',' ')+')')
    row.click(); pg.wait_for_url('**/health/**')
    t=pg.locator('main').inner_text(); check('생후 13개월' in t and '다가오는 일정' in t and '지난 일정' in t,'일정 화면')
    pg.screenshot(path=D+'h-1.png',full_page=True)
    first=pg.locator('#sec-next ~ ul .sp-p__who-name').first.inner_text()
    pg.locator('#sec-next ~ ul input[name=done]').first.check(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    pg.locator('summary').click(); pg.locator('details input[name=done]').first.check(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    done=pg.locator('#sec-done ~ ul').inner_text(); check(first in done and str(datetime.date.today().month)+'월' in done,'체크하면 완료에 오늘 날짜 ('+first+')')
    pg.screenshot(path=D+'h-2.png',full_page=True)
    pg.locator('#sec-done ~ ul input[name=done]').first.uncheck(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('저장했어요')")
    check(pg.locator('#sec-done ~ ul input[name=done]').count()==1,'체크 풀면 완료에서 빠짐')
    pg.goto(B+'/settings/children'); pg.get_by_label('앨범에 접종·검진 일정 보기').uncheck(); pg.wait_for_function("document.getElementById('as-live')?.textContent.trim().length>0")
    pg.goto(B+'/home'); check(pg.locator('a[href^="/health/"]').count()==0,'끄면 앨범 위 줄 사라짐')
    b.close()
print('ALL OK')
