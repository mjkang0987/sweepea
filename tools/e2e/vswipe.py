# 크게 보기 스와이퍼(엄빠·가족): 페이지를 다시 안 부르고 넘김, 위 메뉴·아래 판이 그 사진으로, 반응은 넘긴 사진에, 스크립트 없으면 링크
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def swipe_to(pg,i,want):
    pg.locator('.sp-v__track').evaluate(f't=>t.scrollTo({{left:{i}*t.clientWidth}})')
    pg.wait_for_url('**'+want+'**'); pg.wait_for_function(f"document.querySelector('.sp-v__dock form').getAttribute('action').includes('{want.split('/')[-1].split('?')[0]}')")
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    ids=[h.split('/view/')[1] for h in pg.locator('.sp-p__cell-link').evaluate_all('e=>e.map(a=>a.getAttribute("href"))')]
    pg.goto(B+'/view/'+ids[0]); pg.wait_for_selector('.sp-v__track'); pg.evaluate('window.__same=1')
    check(pg.locator('.sp-v__slide').count()==3,'엄빠: 슬라이드 3장')
    check(pg.locator('a[rel=prev]').is_hidden() and not pg.locator('a[rel=next]').is_hidden(),'첫 장: 다음만')
    swipe_to(pg,1,'/view/'+ids[1])
    check(pg.evaluate('window.__same')==1,'밀기: 페이지 다시 안 부름')
    check(pg.locator('.sp-v__pos').inner_text()=='2 / 3','위 메뉴 2 / 3')
    check(pg.get_by_role('link',name='사진 정보 수정').get_attribute('href')=='/photo/'+ids[1],'수정 버튼도 넘긴 사진으로')
    check(not pg.locator('a[rel=prev]').is_hidden(),'가운데: 이전 보임')
    pg.get_by_role('button',name='하트 0개').click(); pg.wait_for_url('**/view/'+ids[1]+'**')
    check(pg.get_by_role('button',name='하트 1개').get_attribute('aria-pressed')=='true','넘긴 사진에 하트')
    pg.wait_for_selector('.sp-v__track'); pg.evaluate('window.__same=1')
    pg.get_by_role('link',name='다음 사진').click(); pg.wait_for_url('**/view/'+ids[2]+'**'); pg.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='3 / 3'")
    check(pg.evaluate('window.__same')==1,'› 화살표도 페이지 다시 안 부름')
    check(pg.locator('a[rel=next]').is_hidden(),'마지막: 다음 없음')
    check(pg.get_by_role('button',name='하트 0개').count()==1,'셋째 사진 하트는 0')
    pg.screenshot(path=S+'vswipe.png')
    # 리뷰 1회차: 빠른 두 번 누르기, 끝에서 포커스, 슬라이드 이름, 불러오는 동안 못 누름
    pg.goto(B+'/view/'+ids[0]); pg.wait_for_selector('.sp-v__track')
    check(pg.locator('.sp-v__slide .sp-v__media').evaluate_all('e=>e.every(i=>i.alt.length>0)'),'슬라이드마다 이름')
    nx=pg.locator('a[rel=next]'); nx.focus(); pg.keyboard.press('Enter'); pg.keyboard.press('Enter')
    pg.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='3 / 3'")
    check(True,'빠르게 두 번 → 3 / 3')
    check(pg.evaluate("document.activeElement.getAttribute('rel')")=='prev','끝에서 › 가 숨으면 포커스는 ‹ 로')
    check(pg.locator('#v-title').get_attribute('aria-live')=='polite','바뀐 사진 알림(제목)')
    pg.route('**/view/*', lambda r: (__import__('time').sleep(1.5), r.continue_()) if r.request.resource_type=='fetch' else r.continue_())
    pg.locator('.sp-v__track').evaluate('t=>t.scrollTo({left:0})'); pg.wait_for_url('**/view/'+ids[0]+'**')
    check(pg.locator('.sp-v__dock').evaluate('e=>e.inert'),'불러오는 동안 아래 판 못 누름')
    pg.wait_for_function("!document.querySelector('.sp-v__dock').inert"); check(True,'다 오면 다시 누를 수 있음')
    pg.unroute('**/view/*')
    # 가족 화면도 같은 스와이퍼
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','큰이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 큰이모').click(); pg.wait_for_url('**done=member-active**')
    gp.goto(B+'/album/'+ids[0]); gp.wait_for_selector('.sp-v__track'); gp.evaluate('window.__same=1')
    swipe_to(gp,1,'/album/'+ids[1])
    check(gp.evaluate('window.__same')==1 and gp.locator('.sp-v__pos').inner_text()=='2 / 3','가족: 밀기 2 / 3, 페이지 다시 안 부름')
    check(gp.get_by_role('button',name='하트 1개').count()==1,'가족: 넘긴 사진의 하트 수(엄빠 1)')
    check(gp.locator('.sp-v__edit').count()==0,'가족: 수정 버튼 없음')
    # 스크립트 없이
    nj=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nj.add_cookies(ctx.cookies()); q=nj.new_page()
    q.goto(B+'/view/'+ids[0]); check(q.locator('.sp-v__track').count()==0,'스크립트 없음: 한 장')
    q.get_by_role('link',name='다음 사진').click(); q.wait_for_url('**/view/'+ids[1]+'**'); check(True,'스크립트 없음: 링크로 넘김')
print('FAILS',fails)
