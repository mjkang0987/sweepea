# 아기 자세히 보기(153): 앨범 머리 아이 이름 → /kid/[id], 기념일·접종 일정·사진·고치기, 접종에서 돌아오면 이 화면
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; S='/tmp/claude-0/-home-user-sweepea/aa46c609-fc0b-5217-be18-d99ce59a51b6/scratchpad/sel/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    link=pg.locator('.sp-p__albumhead-kid-link'); check(link.count()==1 and link.bounding_box()['height']>=24,'앨범 머리 아이 이름이 링크(누르는 높이 24px 이상)')
    link.click(); pg.wait_for_url('**/kid/**'); pg.wait_for_timeout(300); pg.screenshot(path=S+'kid.png')
    t=pg.locator('main').inner_text()
    check(pg.get_by_role('heading',level=1).inner_text()=='하린' and '2025년 9월 17일생' in t and '개월' in t and '태어난 지' in t,'이름·생일·나이·태어난 지')
    check(('다음 기념일' in t and '일 남았어요' in t) or '오늘은' in t,'기념일 카드')
    check(pg.get_by_role('link',name='하린 사진 보기').count()==1 and pg.get_by_role('link',name='이름·생일 고치기').count()==1,'사진 보기·고치기 링크')
    pg.locator('a[href*="from=kid"]').click(); pg.wait_for_url('**/health/**')
    back=pg.locator('.sp-p__back'); check(back.inner_text().strip()=='하린' and '/kid/' in back.get_attribute('href'),'접종 화면 뒤로 → 아기 화면')
    pg.goto(B+'/kid/00000000-0000-4000-8000-000000000000'); check(pg.url.endswith('/home'),'모르는 아이면 앨범으로')
    n=b.new_context().new_page(); n.goto(B+'/kid/x'); check('/kid/' not in n.url,'로그인 안 하면 못 봄')
    b.close()
print('FAILS',FAILS)
