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
    pg.goto(B+'/settings/children/new'); pg.fill('#name','도윤'); pg.fill('#birth','2026-08-30'); pg.get_by_role('button',name='추가').click(); pg.wait_for_url('**done=added**')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    pg.locator('.sp-r__btn').first.click(); pg.wait_for_load_state(); pg.fill('.sp-say .sp-f__input','아이고 우리 하린이 많이 컸네'); pg.get_by_role('button',name='보내기').click(); pg.wait_for_selector('.sp-toast')
    pg.screenshot(path=S+'react-code.png')
    btns=pg.locator('.sp-r__btn').evaluate_all("e=>e.map(b=>{const r=b.getBoundingClientRect(),i=b.querySelector('.sp-r__icon').getBoundingClientRect(),s=b.querySelector('.sp-r__icon').getBoundingClientRect(),n=b.querySelector('.sp-r__n'),e=n?n.getBoundingClientRect().right:i.right;return [Math.round((i.x+e)/2-(r.x+r.width/2)),Math.round(i.y+i.height/2-(r.y+r.height/2)),Math.round(s.width),Math.round(i.width)]})")
    check(all(abs(x)<=1 and abs(y)<=1 and w==iw for x,y,w,iw in btns),'이모지(+수)가 칸 가운데·그림=칸 크기 %s'%btns)
    pg.get_by_role('link',name='사진 정보 수정').click(); pg.wait_for_url('**/photo/**')
    pg.screenshot(path=S+'edit-code.png',full_page=True)
    d=pg.locator('#date').bounding_box(); g=pg.locator('.sp-p__rows').bounding_box()
    check(d['x']+d['width']<=g['x']+g['width'] and pg.get_by_role('heading',level=1).inner_text()=='사진 정보 수정','날짜는 묶음 안, 제목 위 줄')
    sv=pg.get_by_role('button',name='저장').bounding_box(); de=pg.get_by_role('link',name='사진 지우기').bounding_box()
    check(de['y']-(sv['y']+sv['height'])<40,'지우기가 저장 바로 아래 %d'%(de['y']-(sv['y']+sv['height'])))
    pg.fill('#date','2026-01-02'); pg.get_by_label('도윤').check(); pg.get_by_role('button',name='저장').click(); pg.wait_for_function("document.getElementById('ph-live')?.textContent.includes('저장했어요')"); check(True,'저장 → 그 자리에서 토스트')
print('FAILS',fails)
