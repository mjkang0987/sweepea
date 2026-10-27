# 엄빠 앨범 엇갈린 배열: 2줄(휴대폰)·4줄(넓은 화면), 칸 높이=사진 비율, 반응 알약
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
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg',D+'u0.jpg',D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); pg.get_by_role('button',name='하트 0개').click(); pg.wait_for_load_state()
    pg.goto(B+'/home')
    cells=pg.locator('.sp-p__cell').evaluate_all('e=>e.map(c=>{const b=c.getBoundingClientRect();const i=c.querySelector("img");return [Math.round(b.x),Math.round(b.width),Math.round(b.height),i.naturalWidth,i.naturalHeight]})')
    xs=sorted(set(c[0] for c in cells)); check(len(xs)==2,'휴대폰 2줄 %s'%xs)
    ok=all(abs(c[2]-c[1]*min(1.6,max(0.6,c[4]/c[3])))<4 for c in cells if c[3]); check(ok,'칸 높이 = 사진 비율 %s'%cells)
    check(pg.locator('.sp-p__cell-meta').count()==1 and '하트 1개' in pg.locator('.sp-p__cell-img').first.get_attribute('alt'),'하트 받은 칸에 알약·이름')
    h=pg.locator('.sp-p__month-head').first; check(h.locator('h2').inner_text() in ('10월','9월','11월','12월') and '하린 생후' in h.inner_text() and '사진' in h.inner_text(),'달 제목·개월·사진 수 '+h.inner_text().replace('\n',' | '))
    pg.screenshot(path=S+'masonry.png')
    pg.set_viewport_size({'width':1280,'height':900}); pg.reload()
    w=pg.locator('.sp-p__cell').first.evaluate('c=>c.getBoundingClientRect().width'); gw=pg.locator('.sp-p__grid').first.evaluate('g=>g.getBoundingClientRect().width'); check(abs(w-(gw-12)/4)<2,'넓은 화면 4줄 폭 %d/%d'%(w,gw))
    pg.screenshot(path=S+'masonry-pc.png')
print('FAILS',fails)
