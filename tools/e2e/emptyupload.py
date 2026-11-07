# 183 빈 앨범 가운데 '사진 추가하기': 사진 없는 엄빠 홈 안내 아래 버튼 → 올리기, 탭바 캡슐에 안 가림. 거르기로 빈 화면엔 없음 (mock, 인자: 스크린샷 폴더, 엔진)
import sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; W=sys.argv[1] if len(sys.argv)>1 else '/tmp'; eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    for scheme in ['light','dark']:
        pg=br.new_page(viewport={'width':390,'height':844},color_scheme=scheme)
        pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
        pg.fill('#child','하린'); pg.fill('#birth','2025-10-01'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
        pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
        btn=pg.locator('.sp-p__empty').get_by_role('link',name='사진 추가하기')
        check(btn.count()==1,f'{scheme}: 빈 앨범에 사진 추가하기 하나')
        bb=btn.bounding_box(); nb=pg.locator('.sp-p__tabs-pill').bounding_box()
        check(bb['y']+bb['height']<=nb['y'] and bb['height']>=44,f'{scheme}: 버튼이 탭바 위·누르기 충분 {bb}')
        pg.wait_for_timeout(800); pg.screenshot(path=f'{W}/eu-{scheme}.png')
        btn.click(); pg.wait_for_url('**/upload'); check(True,f'{scheme}: 누르면 올리기')
        # 거르기로 빈 화면(영상만): 버튼 없음
        pg.goto(B+'/home?t=video'); check(pg.get_by_role('link',name='사진 추가하기').count()==0,f'{scheme}: 거르기로 빈 화면엔 없음')
        pg.set_viewport_size({'width':1280,'height':900}); pg.goto(B+'/home'); wb=pg.locator('.sp-p__empty-btn').bounding_box()
        check(wb['width']<=352+1 and abs(wb['x']+wb['width']/2-640)<=2,f'{scheme}: 넓은 화면은 레이어 폭·가운데 {wb}')
        pg.close()
    br.close()
print('FAILS',fails)
