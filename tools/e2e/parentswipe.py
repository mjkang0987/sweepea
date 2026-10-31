# 엄빠 앨범 넘겨 보기·모아 보기(98d, 디자인 ParentHomeSwipe, mock). 인자: 임시 폴더 엔진
# 세그먼트로 오가고 고른 보기는 기기에 기억, 넘겨 보기는 가족과 같은 카드(가운데 + 양옆), −/+ 없음,
# 카드를 누르면 크게 보기 → 닫으면 그 카드가 가운데, 옆으로 밀면 다음 60장, 모아 보기로 돌아가면 칸·−/+
import os,sys,struct,tempfile
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else tempfile.gettempdir()
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
SRCS=[open(D+f,'rb').read() for f in ('u0.jpg','u1.jpg','u2.jpg')]
def jpg(path,date,SRC):
    d=date.encode()+b'\0'; o=b'+09:00\0'
    tiff=b'II'+struct.pack('<HI',42,8)+struct.pack('<HHHII',1,0x8769,4,1,26)+struct.pack('<I',0)
    tiff+=struct.pack('<HHHII',2,0x9003,2,20,56)+struct.pack('<HHII',0x9011,2,7,76)+struct.pack('<I',0)+d+o
    app1=b'Exif\0\0'+tiff
    open(path,'wb').write(SRC[:2]+b'\xff\xe1'+struct.pack('>H',len(app1)+2)+app1+SRC[2:])
# 70장(쪽 경계 60을 넘게), 찍은 날이 모두 달라 순서가 정해짐
FILES=[]
for i in range(70):
    f=os.path.join(W,f'ps-{i:02d}.jpg')
    if not os.path.exists(f): jpg(f,f'2024:{1+i//28:02d}:{1+i%28:02d} 10:00:00',SRCS[i%3])
    FILES.append(f)
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
CENTER="(id)=>{const s=document.querySelector('.sp-a__swipe').getBoundingClientRect(),c=document.getElementById(id).querySelector('.sp-a__card').getBoundingClientRect();return Math.abs((c.left+c.width/2)-(s.left+s.width/2))}"
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    pg=br.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2023-12-01'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    check(pg.get_by_role('navigation',name='보기 방식').count()==0,'사진 없으면 보기 세그먼트 없음')
    for k in range(0,len(FILES),50):
        pg.goto(B+'/upload'); pg.set_input_files('#up-files',FILES[k:k+50]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=300000)
        pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=300000)
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__cell-img')
    seg=pg.get_by_role('navigation',name='보기 방식')
    check(seg.get_by_role('link',name='모아 보기').get_attribute('aria-current')=='page','처음은 모아 보기(지금까지와 같게)')
    # 1) 넘겨 보기로
    seg.get_by_role('link',name='넘겨 보기').click(); pg.wait_for_url('**v=swipe**'); pg.wait_for_selector('.sp-a__card-img')
    check(pg.get_by_role('navigation',name='보기 방식').get_by_role('link',name='넘겨 보기').get_attribute('aria-current')=='page','넘겨 보기 눌림 표시')
    check(pg.locator('.sp-p__zoom').count()==0 and pg.locator('.sp-p__cell').count()==0,'넘겨 보기엔 −/+·칸 없음')
    slides=pg.locator('.sp-a__slide'); check(slides.count()==60,f'처음 60장 카드 ({slides.count()})')
    first=slides.first.get_attribute('id')
    check(pg.evaluate(CENTER,first)<2,'첫 카드가 가운데')
    pos=slides.first.locator('.sp-a__pos').inner_text(); check(pos.startswith('1 / 70'),f'자리 1 / 70 ({pos})')
    lab=slides.first.locator('.sp-a__card').get_attribute('aria-label'); check(lab.endswith('사진 크게 보기') and '2024년' in lab,f'카드 이름 ({lab})')
    box=slides.first.locator('.sp-a__card').bounding_box(); check(abs(box['width']-290)<1 and abs(box['height']-360)<1,f'카드 290×360 {box}')
    op=slides.nth(1).locator('.sp-a__card').evaluate("e=>+getComputedStyle(e).opacity")
    if eng=='chromium': check(op<0.9,f'옆 카드는 흐리게 ({op})')
    check(pg.locator('.sp-p__albumhead-sub').inner_text()=='사진 70','머리 작은 줄은 사진 수')
    pg.screenshot(path=W+'/ps-swipe.png')
    # 2) 기억: 주소 없이 다시 열어도 넘겨 보기
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-a__card-img, .sp-p__cell-img')
    check(pg.locator('.sp-a__swipe').count()==1,'다시 열어도 넘겨 보기(기기에 기억)')
    # 3) 옆으로 밀면 다음 쪽(60 → 70)
    pg.locator('.sp-a__swipe').evaluate("e=>e.scrollTo({left:e.scrollWidth})")
    pg.wait_for_function("document.querySelectorAll('.sp-a__slide').length===70",timeout=20000)
    ids=pg.eval_on_selector_all('.sp-a__slide','e=>e.map(x=>x.id)'); check(len(set(ids))==70,'다음 쪽 이어 붙임, 겹침 없음')
    check(pg.locator('.sp-a__slide').last.locator('.sp-a__pos').inner_text().startswith('70 / 70'),'마지막 카드 70 / 70')
    # 첫 쪽 밖(65번째) 카드에서 크게 보기 → 닫으면 그 카드까지 그려서 가운데, 큰 사진은 그 카드 둘레만 바로 받음
    far=pg.locator('.sp-a__slide').nth(64); fid=far.get_attribute('id')
    far.evaluate("e=>e.scrollIntoView({inline:'center',block:'nearest'})"); pg.wait_for_timeout(400)
    far.locator('.sp-a__card').click(); pg.wait_for_url('**/view/'+fid[2:]+'**')
    pg.get_by_role('link',name='닫기').first.click(); pg.wait_for_url('**to='+fid[2:]+'**'); pg.wait_for_selector('#'+fid); pg.wait_for_timeout(600)
    check(pg.evaluate(CENTER,fid)<2,f'첫 쪽 밖 카드도 닫으면 가운데 ({pg.evaluate(CENTER,fid)})')
    check(pg.locator('#'+fid+' .sp-a__pos').inner_text().startswith('65 / 70'),'돌아와도 자리 65 / 70')
    ld=pg.eval_on_selector_all('.sp-a__card-img','e=>e.map(x=>x.loading)')
    check(ld[64]=='eager' and ld[0]=='lazy' and ld.count('eager')==3,f'돌아온 카드 둘레 3장만 바로 받음 ({ld.count("eager")})')
    # 4) 카드를 누르면 크게 보기, 닫으면 그 카드가 가운데
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-a__swipe')
    third=pg.locator('.sp-a__slide').nth(2); tid=third.get_attribute('id')
    third.evaluate("e=>e.scrollIntoView({inline:'center',block:'nearest'})"); pg.wait_for_timeout(400)
    third.locator('.sp-a__card').click(); pg.wait_for_url('**/view/'+tid[2:]+'**')
    check('z=' not in pg.url,'크게 보기 주소에 칸 단계 없음')
    pg.get_by_role('link',name='닫기').first.click(); pg.wait_for_url('**/home**'); pg.wait_for_selector('.sp-a__swipe'); pg.wait_for_timeout(600)
    check(pg.evaluate(CENTER,tid)<2,f'닫으면 그 카드가 가운데 ({pg.evaluate(CENTER,tid)})')
    # 5) 모아 보기로 돌아가면 칸·−/+, 기억도 모아 보기
    pg.get_by_role('navigation',name='보기 방식').get_by_role('link',name='모아 보기').click(); pg.wait_for_url('**v=list**'); pg.wait_for_selector('.sp-p__cell-img')
    check(pg.locator('.sp-p__zoom').count()==1 and pg.locator('.sp-a__swipe').count()==0,'모아 보기: 칸·−/+')
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-a__card-img, .sp-p__cell-img'); check(pg.locator('.sp-a__swipe').count()==0,'모아 보기 누른 뒤 다시 열어도 모아 보기')
    # 다른 창에서 넘겨 보기를 골라 쿠키가 바뀌어도 −/+는 칸 단계로(리뷰 2026-10-31)
    other=pg.context.new_page(); other.goto(B+'/home?v=swipe'); other.wait_for_selector('.sp-a__swipe'); other.close()
    pg.get_by_role('link',name='작게(한 줄에 더 많이)').click(); pg.wait_for_url('**z=3**'); pg.wait_for_selector('.sp-p__grid--z3 .sp-p__cell-img')
    check(pg.locator('.sp-a__swipe').count()==0 and pg.locator('.sp-p__zoom').count()==1,'다른 창에서 넘겨 보기를 골라도 −/+는 칸으로')
    # 6) 스크립트 없이도 넘겨 보기·다음 쪽 링크
    nj=br.new_context(viewport={'width':390,'height':844},java_script_enabled=False,storage_state=pg.context.storage_state()).new_page()
    nj.goto(B+'/home?v=swipe'); check(nj.locator('.sp-a__slide').count()==60 and nj.locator('[data-more] a').get_attribute('href').count('v=swipe')==1,'스크립트 없어도 카드·사진 더 보기 링크')
    nj.locator('[data-more] a').click(); nj.wait_for_url('**before=**')
    check(nj.locator('.sp-a__slide').count()==10 and nj.locator('.sp-a__pos').first.inner_text().startswith('61 / 70'),'링크로 다음 쪽: 10장, 61 / 70부터')
    br.close()
print('FAILS',fails)
