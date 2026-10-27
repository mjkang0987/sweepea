# 한마디: 판 안 한 줄(이름 + 글 말줄임 + 수) → 누르면 아래 시트(목록·입력칸). 엄빠·가족 다 본다. 넘기면 그 사진 것으로 바뀐다
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    vid=pg.url.split('/view/')[1].split('?')[0]
    check(pg.locator('.sp-v__talk').count()==0 and pg.locator('#talk').count()==0,'한마디 없으면 줄·시트 없음')
    check(pg.locator('.sp-v__meta').inner_text().strip()!='' and pg.locator('.sp-v__meta button').count()==0,'날짜 줄엔 날짜만(하트 중복 없음)')
    check(pg.locator('.sp-r__btn').count()==5,'반응 알약 5개(하트 포함)')
    for t in ['첫 번째 한마디','두 번째 한마디']:
        pg.fill('#say-body','%s'%t); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    line=pg.locator('.sp-v__talk')
    check('두 번째 한마디' in line.inner_text() and '엄마' in line.inner_text(),'엄빠: 한 줄에 최근 것')
    # 가족 들이기
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할아버지'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할아버지').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+'/album/'+vid)
    gp.fill('#say-body','아이고 우리 하린이 많이 컸네 정말 많이 컸어 언제 이렇게 컸니'); gp.locator('#say').get_by_role('button',name='보내기').click(); gp.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    line=gp.locator('.sp-v__talk')
    check(line.get_attribute('aria-haspopup')=='dialog','한 줄은 시트를 연다고 알림')
    name=gp.get_by_role('link',name='한마디 3개 모두 보기')
    check(name.count()==1,'접근 이름에 \'한마디 3개 모두 보기\'')
    txt=gp.locator('.sp-v__talk-text'); check(txt.evaluate('e=>e.scrollWidth>e.clientWidth'),'긴 글은 한 줄 말줄임')
    hb=line.bounding_box(); check(43<=hb['height']<=70,f'한 줄 높이 {hb["height"]}')
    rb=gp.locator('.sp-r__btn').first.bounding_box(); check(40<=rb['height']<=48,f'알약 높이 {rb["height"]}')
    ib=gp.locator('.sp-r__icon').first.bounding_box(); check(18<=ib['width']<=24,f'이모지 {ib["width"]}px')
    gp.screenshot(path=S+'cm-family.png')
    # 시트 열기
    line.click(); sheet=gp.locator('#talk')
    check(sheet.evaluate('e=>e.open && e.matches(":modal")'),'누르면 모달 시트')
    items=gp.locator('.sp-v__sheet-item')
    check(items.count()==3 and '외할아버지' in items.nth(0).inner_text() and '엄마' in items.nth(2).inner_text(),'시트: 3개 최근 순')
    check(gp.get_by_role('heading',name='한마디 3개').is_visible(),'시트 제목')
    sb=sheet.bounding_box(); check(abs(sb['y']+sb['height']-844)<=1,'시트는 화면 아래에 붙음')
    gp.screenshot(path=S+'cm-sheet.png')
    gp.keyboard.press('Escape'); check(not sheet.evaluate('e=>e.open'),'Esc로 닫힘')
    check(gp.evaluate('document.activeElement.classList.contains("sp-v__talk")'),'닫으면 한 줄로 초점 돌아옴')
    line.click(); gp.get_by_role('link',name='닫기').last.click(); check(not sheet.evaluate('e=>e.open'),'닫기로 닫힘')
    line.click(); gp.mouse.click(195,60); check(not sheet.evaluate('e=>e.open'),'바깥 누르면 닫힘')
    # 시트 안에서 보내기
    line.click(); gp.fill('#say-body-talk','시트에서 보냄'); gp.locator('#say-talk').get_by_role('button',name='보내기').click(); gp.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    check('시트에서 보냄' in gp.locator('.sp-v__talk').inner_text(),'시트에서 보낸 것이 맨 위')
    check(gp.locator('#talk').evaluate("e=>e.matches(':modal')") and '시트에서 보냄' in gp.locator('.sp-v__sheet-item').first.inner_text(),'시트에서 보내면 시트 열린 채 맨 위에 보임')
    gp.keyboard.press('Escape')
    # 넘기면 그 사진 것(한마디 없음)으로
    gp.get_by_role('link',name='다음 사진').click(); gp.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='2 / 2'")
    check(gp.locator('.sp-v__talk').count()==0,'넘긴 사진엔 한마디 줄 없음')
    check(len(gp.evaluate("sel=>[...document.querySelectorAll(sel)].flatMap(e=>e.getAnimations().map(a=>a.animationName))",'.sp-v__panel .sp-r__icon'))==5,'넘긴 사진에서 이모지 다시 한 번')
    gp.get_by_role('link',name='이전 사진').click(); gp.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='1 / 2'")
    gp.locator('.sp-v__talk').click(); check(gp.locator('#talk').evaluate('e=>e.open'),'돌아온 뒤에도 시트 열림(바뀐 판에서)')
    gp.keyboard.press('Escape')
    # 넘겨 보기 카드: 카드 아래 하트 없음, 반응 줄 5개(수)
    gp.goto(B+'/album'); gp.wait_for_timeout(500)
    sl=gp.locator('.sp-a__slide').first
    check(not sl.locator('.sp-a__card-cap button').first.is_visible() and sl.locator('.sp-a__slide-react .sp-r__btn').count()==5,'넘겨 보기: 카드 하트 안 보임, 반응 5개')
    gp.screenshot(path=S+'cm-swipe.png')
    check(gp.evaluate("sel=>[...document.querySelectorAll(sel)].flatMap(e=>e.getAnimations().map(a=>a.animationName))",'.sp-a__slide .sp-r__icon')==[],'넘겨 보기 카드 이모지는 멈춤')
    check(not sl.locator('.sp-a__card-heart').is_visible(),'스크롤 애니메이션 되는 브라우저: 카드 하트 숨김(중복 없음)')
    # 안 되는 브라우저 흉내: 반응 줄 숨기고 카드 하트 보이기 → 눌러서 하트
    old_css='.sp-a__slide-react{display:none!important}.sp-a__card-heart{display:block!important;margin-inline-start:auto}.sp-a__card-heart .sp-r__btn{padding:0 12px;background:var(--fill)}.sp-a__card-heart .sp-r__btn[aria-pressed=true]{background:var(--pea-tint)}'
    gp.add_style_tag(content=old_css)
    h=sl.locator('.sp-a__card-heart .sp-r__btn'); check(h.count()==1 and h.is_visible(),'옛 브라우저: 카드에 하트 하나')
    check(sl.locator('.sp-a__card-heart h2').count()==0 and sl.locator('.sp-a__card-heart form').get_attribute('aria-labelledby') is None,'카드 하트엔 숨은 제목·이름표 없음')
    hb=h.bounding_box(); check(hb['height']>=44 and hb['width']>=44,f'카드 하트 크기 {hb}')
    h.click(); gp.wait_for_load_state(); gp.add_style_tag(content=old_css)
    gp.screenshot(path=S+'cm-swipe-old.png')
    check(gp.locator('.sp-a__slide').first.locator('.sp-a__card-heart .sp-r__btn').get_attribute('aria-label')=='하트 1개','카드 하트 누르면 1개')
    gp.locator('.sp-a__slide').first.locator('.sp-a__card-heart .sp-r__btn').click(); gp.wait_for_load_state()
    # 좁은 화면(320)·큰 글씨: 알약이 넘치지 않음
    gp.set_viewport_size({'width':320,'height':700}); gp.goto(B+'/album/'+vid)
    over=gp.locator('.sp-r__btn').evaluate_all('e=>e.filter(b=>b.scrollWidth>b.clientWidth+1).length'); check(over==0,'320px에서 알약 안 넘침')
    gp.set_viewport_size({'width':390,'height':844})
    # 엄빠 화면·수정 화면
    pg.goto(B+'/view/'+vid)
    check('시트에서 보냄' in pg.locator('.sp-v__talk').inner_text(),'엄빠: 가족 한마디 한 줄')
    pg.screenshot(path=S+'cm-parent.png')
    pg.goto(B+'/photo/'+vid); check('외할아버지' in pg.locator('.sp-p__thumbbox-say').inner_text(),'수정 화면 말풍선도 같은 최근 한마디')
    # 스크립트 없으면 #talk로 판 안에 펼쳐짐
    nj=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nj.add_cookies(gp.context.cookies()); n=nj.new_page()
    n.goto(B+'/album/'+vid); n.locator('.sp-v__talk').click(); check(n.locator('.sp-v__sheet-item').first.is_visible(),'스크립트 없어도 목록 보임')
    # 남은 못 봄
    x=b.new_context().new_page(); x.goto(B+'/album/'+vid); check(x.locator('.sp-v__talk').count()==0,'남은 못 봄')
    dk=b.new_context(viewport={'width':390,'height':844},color_scheme='dark')
    dk.add_cookies(gp.context.cookies()); d=dk.new_page(); d.goto(B+'/album/'+vid); d.screenshot(path=S+'cm-family-dark.png')
    d.locator('.sp-v__talk').click(); d.screenshot(path=S+'cm-sheet-dark.png')
print('FAILS',fails)
