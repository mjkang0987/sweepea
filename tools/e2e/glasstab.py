# 떠 있는 유리 탭바(102): 캡슐이 화면 아래에서 떠 있고(양옆 여백), 옆에 둥근 '사진 추가', 홈엔 아이 카드·떠 있던 '사진 추가하기' 없음.
# 접종은 알림 탭 '다가오는 일정'(2주 안)·설정 › 아이 '접종·검진 일정' 줄로, 거기서 들어가면 돌아가기도 그쪽. 아래 막대·토스트가 탭바에 안 가림 (mock, 인자: 스크린샷 폴더, 엔진)
import sys,datetime
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; W=sys.argv[1] if len(sys.argv)>1 else '/tmp'; eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
H=844
# 생후 11개월 2주쯤: 12개월 접종이 2주 안에 다가옴
birth=(datetime.date.today()-datetime.timedelta(days=355)).isoformat()
with sync_playwright() as p:
    br=getattr(p,eng).launch(); pg=br.new_page(viewport={'width':390,'height':H})
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth',birth); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    nav=pg.locator('.sp-p__tabs'); pill=pg.locator('.sp-p__tabs-pill'); add=pg.get_by_role('link',name='사진 추가')
    nb=pill.bounding_box(); ab=add.bounding_box()
    check(nb['x']>=19 and nb['y']+nb['height']<=H-7,f'캡슐이 떠 있음(양옆·아래 여백) {nb}')
    check(abs(nb['height']-64)<=2,'캡슐 높이 4rem')
    check(ab['x']>nb['x']+nb['width'] and abs(ab['width']-64)<=2,'캡슐 오른쪽에 둥근 사진 추가')
    check(pill.evaluate("e=>getComputedStyle(e).backdropFilter||getComputedStyle(e).webkitBackdropFilter").find('blur')>=0,'캡슐 유리(흐림)')
    check(pg.locator('.sp-p__fab').count()==0 and pg.locator('.sp-p__kid').count()==0,'홈에 떠 있던 사진 추가하기·아이 카드 없음')
    check(pg.locator('.sp-p__tab[aria-current=page]').evaluate("e=>getComputedStyle(e).backgroundColor")!='rgba(0, 0, 0, 0)','지금 탭 둥근 강조')
    pg.screenshot(path=W+'/gt-home.png')
    add.click(); pg.wait_for_url('**/upload'); check(True,'사진 추가 누르면 올리기')
    # 알림 탭: 다가오는 일정
    pg.goto(B+'/reactions'); soon=pg.locator('.sp-p__soon')
    check(soon.count()==1 and '하린' in soon.inner_text(),f'알림 탭 다가오는 일정 카드 {soon.count()}')
    pg.screenshot(path=W+'/gt-alerts.png')
    soon.click(); pg.wait_for_url('**/health/**')
    back=pg.locator('.sp-p__back'); check(back.inner_text()=='알림' and back.get_attribute('href')=='/reactions','알림에서 오면 돌아가기도 알림')
    check(pg.locator('.sp-p__tab[aria-current=page]').inner_text().strip()=='알림','알림 탭이 지금 탭')
    # 설정 › 아이
    pg.goto(B+'/settings/children'); line=pg.locator('.sp-p__kid-health')
    check(line.count()==1 and '접종·검진 일정' in line.inner_text(),'아이 줄 아래 접종·검진 일정')
    check('알림 탭에 다가오는 일정 보기' in pg.content(),'스위치 이름 바뀜')
    pg.screenshot(path=W+'/gt-children.png')
    line.click(); pg.wait_for_url('**/health/**'); check(pg.locator('.sp-p__back').inner_text()=='아이','설정에서 오면 돌아가기도 아이')
    # 체크하고 저장(스크립트 없이 폼)해도 돌아가기 유지
    # 아래 막대 있는 탭 화면: 막대가 캡슐 위
    pg.goto(B+'/settings/family/sms'); bar=pg.locator('.sp-p__savebar')
    if bar.count():
        bb=bar.bounding_box(); nb=pill.bounding_box(); check(bb['y']+bb['height']<=nb['y']+1,'아래 막대가 캡슐 위')
        pg.screenshot(path=W+'/gt-sms.png')
    pg.goto(B+'/settings'); pg.screenshot(path=W+'/gt-settings.png')
    # 마지막 줄이 캡슐 밑에 숨지 않음
    pg.evaluate("window.scrollTo(0,document.documentElement.scrollHeight)")
    last=pg.locator('.sp-p__version'); lb=last.bounding_box(); nb=pill.bounding_box()
    check(lb['y']+lb['height']<=nb['y'],'설정 마지막 줄이 캡슐 위')
    # 넓은 화면: 위 메뉴
    pg.set_viewport_size({'width':1280,'height':900}); pg.goto(B+'/home')
    nb=nav.bounding_box(); check(nb['y']<=1,'넓은 화면은 위 메뉴')
    pg.screenshot(path=W+'/gt-wide.png')
    br.close()
print('FAILS',fails)
