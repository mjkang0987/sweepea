# 아래 고정 버튼(사용자 2026-10-29 "사파리 하단 바 고려"): 탭 없는 화면은 맨 아래(safe-area만큼 올림), 탭 있는 화면은 탭바 위.
# 내용이 길어도 버튼이 화면 안에 보이고, 마지막 칸이 막대 밑에 숨지 않는다. 올리기는 아래 진행 막대 없이 상태 칸이 차오른다 (mock)
import os,sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
H=844
def bar_at_bottom(pg,sel,gap,msg):
    bb=pg.locator(sel).bounding_box()
    check(bb and abs(bb['y']+bb['height']-(H-gap))<=2,f'{msg} (아래 {H-bb["y"]-bb["height"]:.0f}px)' if bb else msg)
def last_clear(pg,sel_last,sel_bar,msg):
    pg.evaluate("window.scrollTo(0,document.documentElement.scrollHeight)")
    l=pg.locator(sel_last).bounding_box(); b=pg.locator(sel_bar).bounding_box()
    check(l['y']+l['height']<=b['y'],msg)
with sync_playwright() as p:
    br=p.chromium.launch()
    ctx=br.new_context(viewport={'width':390,'height':H}); pg=ctx.new_page()
    # 소개(탭 없음): 맨 아래
    pg.goto(B+'/start'); bar_at_bottom(pg,'.sp-p__savebar',0,'소개: 버튼 막대가 화면 맨 아래')
    check(pg.locator('.sp-p__dots').bounding_box()['y']+12<=pg.locator('.sp-p__savebar').bounding_box()['y'],'소개: 점은 막대 위')
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    bar_at_bottom(pg,'.sp-p__savebar',0,'처음 설정: 다음 막대 맨 아래')
    last_clear(pg,'#birth','.sp-p__savebar','처음 설정: 마지막 칸이 막대 밑에 안 숨음')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    bar_at_bottom(pg,'.sp-p__savebar',0,'비밀번호 정하기: 막대 맨 아래')
    last_clear(pg,'#hint','.sp-p__savebar','비밀번호 정하기: 힌트 칸이 막대 밑에 안 숨음')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    # 올리기(탭 없음, 버튼 둘)
    pg.goto(B+'/upload'); bar_at_bottom(pg,'#up-actions',0,'올리기: 버튼 둘 막대 맨 아래')
    check(pg.locator('#up-bar').evaluate("e=>e.classList.contains('sp-vh')"),'올리기: 진행 막대는 화면에서 숨김(화면 읽기용만)')
    pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    last_clear(pg,'.sp-p__up-note','#up-actions','올리기: 안내 글이 막대 밑에 안 숨음')
    # 그룹을 다 끄고 누르면 화면 밖 알림 칸이 보이게 스크롤
    pg.evaluate("window.scrollTo(0,0)")
    for c in pg.locator('input[name=group]:checked').all(): c.uncheck()
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_timeout(400)
    ab=pg.locator('#up-alert').bounding_box(); bar=pg.locator('#up-actions').bounding_box()
    check(ab and ab['y']>=0 and ab['y']+ab['height']<=bar['y']+1,'그룹 없이 누르면 알림 칸이 막대 위에 보임')
    for c in pg.locator('input[name=group]').all(): c.check()
    pg.evaluate("window.scrollTo(0,0)")
    # 올리는 중 상태 칸 배경이 차오르는지(느린 네트워크로 잡아 둔다)
    pg.route('**/api/media/**',lambda r:(pg.wait_for_timeout(400),r.continue_()))
    pg.get_by_role('button',name='보내지 않고 올리기만').click()
    pg.wait_for_function("document.getElementById('up-status').textContent.includes('올리는 중')",timeout=20000)
    st=pg.locator('#up-status')
    bg=st.evaluate("e=>getComputedStyle(e).backgroundImage")
    check('gradient' in bg,'올리는 중: 상태 칸 배경이 진행 막대(그라디언트)')
    pg.screenshot(path=W+'/bb-upload.png')
    sb=st.bounding_box(); check(sb['y']>=0 and sb['y']+sb['height']<=pg.locator('#up-actions').bounding_box()['y']+1,'올리기 시작하면 상태 칸이 막대 위에 보임')
    pg.wait_for_url('**/home**',timeout=60000)
    pg.unroute('**/api/media/**')
    # 넓은 화면: 버튼은 오른쪽 칸 안 제자리
    pg.set_viewport_size({'width':1280,'height':900}); pg.goto(B+'/upload')
    check(pg.locator('#up-actions').evaluate("e=>getComputedStyle(e).position")=='static','넓은 화면 올리기: 버튼 제자리(고정 안 함)')
    # 낮은 화면(가로로 든 폰): 고정 풀림
    pg.set_viewport_size({'width':844,'height':390}); pg.goto(B+'/upload')
    check(pg.locator('#up-actions').evaluate("e=>getComputedStyle(e).position")=='static','낮은 화면: 막대 고정 풀림')
    pg.set_viewport_size({'width':390,'height':H})
    # 문자 공유(탭 있음): 가족이 없으면 막대 없음
    pg.goto(B+'/settings/family/sms'); check(pg.locator('.sp-p__savebar').count()==0 and 'sp-p--savebar' not in pg.locator('main').get_attribute('class'),'문자 공유: 들어온 가족 없으면 막대 없음')
    # 가족 비밀번호(가족 화면): 맨 아래 고정
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=br.new_context(viewport={'width':390,'height':H}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**')
    bar_at_bottom(gp,'.sp-f__bottom--fixed',0,'가족 비밀번호: 들어가기 막대 맨 아래')
    last_clear(gp,'#pw','.sp-f__bottom--fixed','가족 비밀번호: 입력칸이 막대 밑에 안 숨음')
    gp.wait_for_timeout(800); gp.screenshot(path=W+'/bb-family.png')
    # 글자 200%(가족 아주 크게와 별개로 브라우저 확대): 막대가 화면 안
    gp.evaluate("document.documentElement.style.fontSize='200%'")
    bb=gp.locator('.sp-f__bottom--fixed').bounding_box(); check(bb['y']>=0 and bb['y']+bb['height']<=H+1,'글자 200%: 막대가 화면 안')
    gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    # 문자 공유: 승인한 가족이 있으면 탭바 위
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    pg.goto(B+'/settings/family/sms'); tab=pg.locator('.sp-p__tabs').bounding_box()
    bar_at_bottom(pg,'.sp-p__savebar',H-tab['y'],'문자 공유: 링크 만들기 막대가 탭바 바로 위')
    pg.screenshot(path=W+'/bb-sms.png')
    br.close()
print('FAILS',fails) if fails else print('ALL OK')
