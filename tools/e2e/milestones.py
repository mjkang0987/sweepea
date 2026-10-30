# 기념일(사용자 2026-10-29 "100일 이벤트, 200일 이벤트 이런 식으로", 50일·100~1000일 백 단위·그다음 돌): 오늘 100일인 아이로
# 엄빠 앨범 가운데 레이어, 오늘 찍은 사진 칸에 '100일' 표시, 머리 날짜 줄 '· 100일', 가족 앨범 맨 위 축하 안내·날짜 제목 '하린 100일' (mock)
import os,sys,datetime,struct
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
today=(datetime.datetime.utcnow()+datetime.timedelta(hours=9)).date()
birth=(today-datetime.timedelta(days=99)).isoformat()
# 오늘 찍은 사진(EXIF 찍은 날 = 오늘 정오, loadmore.py와 같은 방식)
def jpg(path,date,SRC):
    d=date.encode()+b'\0'; o=b'+09:00\0'
    tiff=b'II'+struct.pack('<HI',42,8)+struct.pack('<HHHII',1,0x8769,4,1,26)+struct.pack('<I',0)
    tiff+=struct.pack('<HHHII',2,0x9003,2,20,56)+struct.pack('<HHII',0x9011,2,7,76)+struct.pack('<I',0)+d+o
    app1=b'Exif\0\0'+tiff
    open(path,'wb').write(SRC[:2]+b'\xff\xe1'+struct.pack('>H',len(app1)+2)+app1+SRC[2:])
TODAY=os.path.join(W,'ms-today.jpg'); jpg(TODAY,today.strftime('%Y:%m:%d')+' 12:00:00',open(D+'u0.jpg','rb').read())
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    pg=br.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth',birth); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.wait_for_timeout(500)
    check('태어난 지 100일이에요' in pg.content(),'엄빠 앨범: 오늘 100일 레이어')
    for b in ('닫기','나중에'):
        if pg.get_by_role('button',name=b).count(): pg.get_by_role('button',name=b).first.click(); pg.wait_for_timeout(300)
    # 사진 이름 없는 파일(오늘 시각)로 올리면 오늘 찍은 사진
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[TODAY,D+'u1.jpg'])
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.goto(B+'/home?z=2'); pg.wait_for_selector('.sp-p__cell-img')
    todays=pg.locator(f'.sp-p__cell[data-d="{today.isoformat()}"]')
    marks=pg.locator('.sp-p__cell-mark').all_inner_texts()
    check(todays.count()==1 and (todays.first.get_attribute('data-mark')=='100일' and '100일' in marks),f'오늘 찍은 칸에 100일 표시 ({todays.count()}장, {marks})')
    w=pg.locator('[data-when]').inner_text()
    check(w.endswith('· 100일'),f'머리 날짜 줄에 기념일 ({w})')
    # 가족: 링크로 들어와 승인 → 맨 위 축하 안내
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=br.new_context(viewport={'width':390,'height':844}).new_page(); g.goto(B+'/i/'+code)
    g.fill('#who-name','외할머니'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/password**'); g.fill('#pw','0917'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    g.goto(B+'/album?v=list&z=2'); g.wait_for_timeout(300)
    for btn in ('사진 보기','보기'):
        if g.get_by_role('button',name=btn,exact=True).count(): g.get_by_role('button',name=btn,exact=True).first.click(); g.wait_for_load_state()
    ev=g.locator('.sp-a__event')
    check(ev.count()==1 and '태어난 지 100일이에요' in ev.inner_text(),f'가족 앨범 맨 위 축하 안내 ({ev.all_inner_texts()})')
    dm=g.locator('.sp-a__day-mark').all_inner_texts()
    check(any('하린 100일' in t for t in dm),f'가족 날짜 제목에 기념일 ({dm})')
    g.screenshot(path=W+'/ms-family.png')
    br.close()
print('FAILS',fails)
