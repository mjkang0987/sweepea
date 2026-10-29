# 엄빠 앨범 사진 크기 −/+ (98a, 디자인 ParentHomeZoom): 머리 오른쪽 −/+, 처음 2칸(엇갈린 배열),
# 1·2·3칸 사진 전부 → 월별 달 카드(대표 3장, 누르면 그 달부터 3칸), 끝 단계는 버튼 꺼짐, 고른 단계는 기기에 기억(달 카드로 들어간 쪽은 빼고), 넓은 화면은 2·4·6줄 (mock, 인자: 스크린샷 폴더 엔진)
import os,sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
# 달마다 사진 수가 달라 칸 위치로 세지 않고 격자 줄 수로
COLS="getComputedStyle(document.querySelector('.sp-p__grid')).gridTemplateColumns.split(' ').length"
SQ="[...document.querySelectorAll('.sp-p__cell')].every(c=>{const r=c.getBoundingClientRect();return Math.abs(r.width-r.height)<1})"
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    pg=br.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    check(pg.locator('.sp-p__zoom').count()==0,'사진 없으면 −/+ 없음')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f for f in ['u0.jpg','u1.jpg','u2.jpg','u0.jpg','u1.jpg','u2.jpg']])
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__cell-img')
    small=pg.get_by_role('link',name='작게(한 줄에 더 많이)'); big=pg.get_by_role('link',name='크게(한 줄에 더 적게)')
    check(small.is_visible() and big.is_visible(),'머리에 −/+')
    nav=pg.locator('.sp-p__zoom').bounding_box(); check(nav['x']+nav['width']<=371 and nav['y']<120,f'−/+ 는 머리 오른쪽 {nav}')
    check(pg.locator('.sp-p__grid--z2').count()>0 and pg.evaluate(COLS)==2,'처음은 2칸')
    small.click(); pg.wait_for_url('**z=3**'); pg.wait_for_selector('.sp-p__cell-img')
    check(pg.evaluate(COLS)==3 and pg.evaluate(SQ),'작게 → 3칸 정사각')
    check(pg.locator('.sp-p__cell').count()==6,'3칸도 사진 전부')
    pg.get_by_role('link',name='작게(달마다 대표 사진)').click(); pg.wait_for_url('**z=m**'); pg.wait_for_selector('.sp-p__mcard')
    cards=pg.locator('.sp-p__mcard'); check(cards.count()==2,f'월별: 달 카드 2장 ({cards.count()})')
    first=cards.first.inner_text().replace('\n',' ')
    check('10월' in first and '4장' in first,f'달 카드에 달·장 수 {first}')
    check(pg.locator('.sp-p__mcard').first.locator('.sp-p__mcard-img').count()==3 and pg.locator('.sp-p__mcard').nth(1).locator('.sp-p__mcard-img').count()==2,'대표는 3장까지')
    check(pg.locator('.sp-p__zoom-btn[aria-disabled=true]').inner_text()=='−','월별이면 작게 꺼짐')
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__mcard')
    check(pg.url.endswith('/home'),'다시 열면 고른 단계(월별) 기억')
    pg.locator('.sp-p__mcard').nth(1).click(); pg.wait_for_url('**before=**'); pg.wait_for_selector('.sp-p__cell-img')
    check('z=3' in pg.url and pg.locator('.sp-p__month').first.get_attribute('data-ym').endswith('-09') and pg.evaluate(COLS)==3,'달 카드 → 그 달부터 3칸')
    # 크게 보기에서 닫으면 그 3칸 자리로(기억한 월별로 바뀌지 않음, 리뷰 2026-10-29)
    cid=pg.locator('.sp-p__cell').first.get_attribute('id'); pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    pg.get_by_role('link',name='닫기').first.click(); pg.wait_for_url('**/home**'); pg.wait_for_selector('.sp-p__cell-img')
    check('z=3' in pg.url and pg.locator('#'+cid).count()==1 and pg.evaluate(COLS)==3,'크게 보기에서 닫으면 보던 3칸으로')
    # 사진 정보 수정 등 z 없이 돌아와도(?to=만) 월별 대신 칸으로 그 사진 자리
    pg.goto(B+'/home?to='+cid[2:]); pg.wait_for_selector('.sp-p__cell-img')
    check(pg.locator('#'+cid).count()==1 and pg.locator('.sp-p__mcard').count()==0,'z 없이 돌아와도 월별 대신 칸으로')
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__mcard')
    check(True,'달 카드로 들어간 3칸·닫고 돌아온 쪽은 기억 안 함(다시 열면 월별)')
    for _ in range(3):
        pg.get_by_role('link',name='크게(한 줄에 더 적게)').click(); pg.wait_for_load_state(); pg.wait_for_selector('.sp-p__cell-img')
    check('z=1' in pg.url and pg.evaluate(COLS)==1,'크게 끝까지 → 1칸')
    check(pg.locator('.sp-p__zoom-btn[aria-disabled=true]').inner_text()=='+','1칸이면 크게 꺼짐')
    ok=pg.evaluate("[...document.querySelectorAll('.sp-p__cell')].every(c=>{const r=c.getBoundingClientRect();return Math.abs(r.width/r.height-parseFloat(getComputedStyle(c).getPropertyValue('--ar')))<0.02 && r.width>380})")
    check(ok,'1칸은 화면 폭 한 장, 원래 모양')
    src=pg.locator('.sp-p__cell-img').first.get_attribute('src'); check('thumb' not in src,f'1칸은 큰 사진 {src[:60]}')
    pg.screenshot(path=W+'/pz-1.png')
    # 넓은 화면: 1칸 = 2줄, 3칸 = 6줄
    pg.set_viewport_size({'width':1280,'height':900}); pg.goto(B+'/home?z=1'); pg.wait_for_selector('.sp-p__cell-img')
    check(pg.evaluate(COLS)==2,'넓은 화면 1칸 = 2줄')
    pg.goto(B+'/home?z=3'); pg.wait_for_selector('.sp-p__cell-img')
    check(pg.evaluate(COLS)==6 and pg.evaluate(SQ),'넓은 화면 3칸 = 6줄 정사각')
    pg.goto(B+'/home?z=2'); pg.wait_for_selector('.sp-p__cell-img')
    check(pg.evaluate(COLS)==4,'넓은 화면 2칸 = 4줄(예전 그대로)')
    br.close()
print('FAILS',fails)
