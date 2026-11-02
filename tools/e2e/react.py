# 반응·한마디 검사: 스스로 가족방을 만들어 사진 3장을 올리고, 가족 둘(이모·외할머니)을 들여보낸 뒤(예전엔 visual.py가 mock '하린' 가족에 올린 사진이 있어야 했음)
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/user/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    pp=b.new_context(viewport={'width':390,'height':844}).new_page()
    pp.goto(B+'/login'); pp.get_by_role('link',name='개발용으로 계속하기').click(); pp.wait_for_url('**/setup')
    pp.fill('#child','하린'); pp.fill('#birth','2025-09-17'); pp.get_by_role('button',name='다음').click(); pp.wait_for_url('**/setup/password**')
    pp.fill('#pw','0917'); pp.get_by_role('button',name='시작하기').click(); pp.wait_for_url('**/home')
    pp.goto(B+'/upload')
    w=pp.locator('#up-pick').bounding_box()['width']
    check(w>200,f"올리기 '사진·영상 고르기' 버튼이 가로로 넓게(작은 체크 칸 모양 아님, {w:.0f}px)")
    pp.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg']); pp.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pp.get_by_role('button',name='보내지 않고 올리기만').click(); pp.wait_for_url('**/home**',timeout=30000)
    pp.goto(B+'/settings/family'); pp.get_by_role('button',name='링크 만들기 (가족)').click(); pp.wait_for_selector('#link-url')
    code=pp.locator('#link-url').input_value().rsplit('/',1)[1]
    def join(ctx,name):
        g=ctx.new_page(); g.goto(B+'/i/'+code)
        g.fill('#who-name',name); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/password**'); g.fill('#pw','0917'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/wait')
        pp.goto(B+'/settings/family'); pp.get_by_role('button',name='승인 '+name).click(); pp.wait_for_function(f"document.getElementById('fam-live')?.textContent.includes('승인했어요')")
        g.goto(B+'/album?v=swipe'); return g
    c=b.new_context(viewport={'width':390,'height':844}); pg=join(c,'이모')
    heart=pg.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first
    check(heart.get_attribute('aria-pressed')=='false','처음엔 하트 안 누름')
    heart.click(); pg.wait_for_load_state()
    heart=pg.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first
    check(heart.get_attribute('aria-pressed')=='true' and heart.get_attribute('aria-label').startswith('하트 1개'),'하트 누르면 1개, 눌림')
    # 2026-10-28부터 반응 뒤 주소는 그 카드까지 그리는 /album?…to=<id>#p-<id>(예전 검사는 '/album#p-'만 봐서 늘 실패)
    check('/album' in pg.url and '#p-' in pg.url,'원래 카드로 돌아옴')
    check(not pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').first.is_visible(),'옆 카드 하트는 숨김(옆 사진 누르기와 안 헷갈리게)')
    third=pg.locator('.sp-a__slide').nth(2); third.evaluate("e=>e.scrollIntoView({inline:'center',block:'nearest'})"); pg.wait_for_timeout(400); third.locator('.sp-a__slide-react .sp-r__btn').first.click(); pg.wait_for_load_state(); pg.wait_for_timeout(300)
    box=pg.locator('.sp-a__slide').nth(2).locator('.sp-a__card').bounding_box()
    check(abs(box['x']+box['width']/2-195)<30,'세 번째 카드에 하트 누르면 그 카드가 가운데로 (x=%d)'%box['x'])
    row=pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn')
    row.nth(1).click(); pg.wait_for_load_state(); pg.wait_for_timeout(400)  # 돌아온 쪽에서 그 카드가 가운데로 오는 동안
    check(pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').nth(1).get_attribute('aria-pressed')=='true','최고 누름')
    pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').nth(1).click(); pg.wait_for_load_state()
    check(pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').nth(1).get_attribute('aria-pressed')=='false','다시 누르면 취소')
    pg.get_by_role('link',name='모아 보기').click(); pg.wait_for_load_state()
    check(pg.locator('.sp-a__badge').count()>=1,'모아 보기 칸에 하트 배지')
    pg.locator('.sp-a__cell-link').first.click(); pg.wait_for_load_state()
    pg.fill('#say-body','많이 컸네'); pg.get_by_role('button',name='보내기').click(); pg.wait_for_load_state(); pg.wait_for_timeout(500)
    # 지금은 스크립트가 그 자리에서 보내 주소가 안 바뀜(예전 검사는 '#say' 주소를 기다림)
    check('보냈어요' in pg.content(),'한마디 보냄')
    pg.fill('#say-body','   '); pg.get_by_role('button',name='보내기').click(); pg.wait_for_load_state(); pg.wait_for_timeout(500)
    check('한마디를 써 주세요' in pg.content(),'빈 한마디 안내')
    mid=pg.url.split('/album/')[1].split('?')[0].split('#')[0]
    r=c.request.post(B+'/album/'+mid,form={'react':'heart:on','back':'//evil.example/x'},max_redirects=0)
    check(r.status==303 and r.headers['location'].startswith('/album/'),'다른 사이트로 돌려보내기 막음')
    r=c.request.post(B+'/album/'+mid,form={'react':'heart:on'},headers={'origin':'https://evil.example'},max_redirects=0)
    check(r.status==403,'다른 출처 폼 POST 막음(checkOrigin)')
    # 다른 사람 기기
    d=b.new_context(viewport={'width':390,'height':844}); dp=join(d,'외할머니')
    h=dp.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first
    check(h.get_attribute('aria-pressed')=='false' and h.get_attribute('aria-label').startswith('하트 1개'),'다른 가족에겐 하트 1개, 안 눌림')
    b.close()
print('ALL OK')
