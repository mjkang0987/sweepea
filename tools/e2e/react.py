# 반응·한마디 검사 (visual.py로 사진을 올린 뒤)
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name='이모',exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    heart=pg.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first
    check(heart.get_attribute('aria-pressed')=='false','처음엔 하트 안 누름')
    heart.click(); pg.wait_for_load_state()
    heart=pg.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first
    check(heart.get_attribute('aria-pressed')=='true' and heart.get_attribute('aria-label').startswith('하트 1개'),'하트 누르면 1개, 눌림')
    check('/album#p-' in pg.url,'원래 카드로 돌아옴')
    check(not pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').first.is_visible(),'옆 카드 하트는 숨김(옆 사진 누르기와 안 헷갈리게)')
    third=pg.locator('.sp-a__slide').nth(2); third.evaluate("e=>e.scrollIntoView({inline:'center',block:'nearest'})"); pg.wait_for_timeout(400); third.locator('.sp-a__slide-react .sp-r__btn').first.click(); pg.wait_for_load_state(); pg.wait_for_timeout(300)
    box=pg.locator('.sp-a__slide').nth(2).locator('.sp-a__card').bounding_box()
    check(abs(box['x']+box['width']/2-195)<30,'세 번째 카드에 하트 누르면 그 카드가 가운데로 (x=%d)'%box['x'])
    row=pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn')
    row.nth(1).click(); pg.wait_for_load_state()
    check(pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').nth(1).get_attribute('aria-pressed')=='true','최고 누름')
    pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').nth(1).click(); pg.wait_for_load_state()
    check(pg.locator('.sp-a__slide').nth(2).locator('.sp-a__slide-react .sp-r__btn').nth(1).get_attribute('aria-pressed')=='false','다시 누르면 취소')
    pg.get_by_role('link',name='모아 보기').click(); pg.wait_for_load_state()
    check(pg.locator('.sp-a__badge').count()>=1,'모아 보기 칸에 하트 배지')
    pg.locator('.sp-a__cell-link').first.click(); pg.wait_for_load_state()
    pg.fill('#say-body','많이 컸네'); pg.get_by_role('button',name='보내기').click(); pg.wait_for_load_state()
    check('보냈어요' in pg.content() and '#say' in pg.url,'한마디 보냄')
    pg.fill('#say-body','   '); pg.get_by_role('button',name='보내기').click(); pg.wait_for_load_state()
    check('한마디를 써 주세요' in pg.content(),'빈 한마디 안내')
    mid=pg.url.split('/album/')[1].split('?')[0].split('#')[0]
    r=c.request.post(B+'/album/'+mid,form={'react':'heart:on','back':'//evil.example/x'},max_redirects=0)
    check(r.status==303 and r.headers['location'].startswith('/album/'),'다른 사이트로 돌려보내기 막음')
    r=c.request.post(B+'/album/'+mid,form={'react':'heart:on'},headers={'origin':'https://evil.example'},max_redirects=0)
    check(r.status==403,'다른 출처 폼 POST 막음(checkOrigin)')
    # 다른 사람 기기
    d=b.new_context(); dp=d.new_page(); dp.goto(B+'/i/Harin001'); dp.get_by_role('button',name='외할머니',exact=True).click(); dp.wait_for_url('**/password**'); dp.fill('#pw','1234'); dp.get_by_role('button',name='들어가기').click(); dp.wait_for_url('**/album')
    h=dp.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first
    check(h.get_attribute('aria-pressed')=='false' and h.get_attribute('aria-label').startswith('하트 1개'),'다른 가족에겐 하트 1개, 안 눌림')
    b.close()
print('ALL OK')
