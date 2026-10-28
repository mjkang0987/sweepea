# 아래로 내리면 60장씩 더 불러오기(88, mock): 사진 130장(6월 30·5월 70·4월 30, EXIF 날짜)으로 쪽 경계에 달이 걸치게.
# 5월 15일 하루 30장(전체 51~80번째)이 첫 쪽 경계에 걸쳐 가족 모아 보기 합치기(89, 엇갈린 배열이라 앞 칸이 안 움직임)를 본다
# 홈: 처음 60장 → 내리면 120 → 130 + '처음 사진까지 모두 봤어요', 걸친 달은 한 묶음·사진 수는 처음부터 그 달 전체, 엇갈린 배열 안 겹침
# 스크립트 없으면 '사진 더 보기' 링크로 다음 60장. 크게 보기에서 닫으면 보던 자리(같은 높이)로
import os,sys,struct,tempfile
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else tempfile.gettempdir()
SRCS=[open(D+f,'rb').read() for f in ('u0.jpg','u1.jpg','u2.jpg','tall.jpg','pano.jpg')]  # 비율 섞기(세로·가로·정사각·아주 긴 것)
def jpg(path,date,SRC):
    d=date.encode()+b'\0'; o=b'+09:00\0'
    tiff=b'II'+struct.pack('<HI',42,8)+struct.pack('<HHHII',1,0x8769,4,1,26)+struct.pack('<I',0)
    tiff+=struct.pack('<HHHII',2,0x9003,2,20,56)+struct.pack('<HHII',0x9011,2,7,76)+struct.pack('<I',0)+d+o
    app1=b'Exif\0\0'+tiff
    open(path,'wb').write(SRC[:2]+b'\xff\xe1'+struct.pack('>H',len(app1)+2)+app1+SRC[2:])
FILES=[]
for m,n in ((6,30),(5,70),(4,30)):
    for i in range(n):
        f=os.path.join(W,f'lm3-{m}-{i:02d}.jpg')
        day=15 if m==5 and 20<=i<50 else 1+i%28
        if m==5 and day==15 and not 20<=i<50: day=16
        if not os.path.exists(f): jpg(f,f'2024:{m:02d}:{day:02d} {10+i%10:02d}:{i%60:02d}:{i%60:02d}',SRCS[(m+i)%5])
        FILES.append(f)
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
def overlap(pg,ym):
    """그 달 칸끼리 겹치는 쌍 수"""
    return pg.evaluate("""ym=>{const r=[...document.querySelectorAll(`.sp-p__month[data-ym="${ym}"] .sp-p__cell`)].map(e=>e.getBoundingClientRect());let n=0;
      for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i],b=r[j];if(a.left<b.right-1&&b.left<a.right-1&&a.top<b.bottom-1&&b.top<a.bottom-1)n++}return n}""",ym)
def bottom(pg):
    pg.evaluate("window.scrollTo(0,document.body.scrollHeight)")
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2024-03-01'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0301'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    for k in range(0,len(FILES),50):
        pg.goto(B+'/upload'); pg.set_input_files('#up-files',FILES[k:k+50]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=300000)
        pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=300000)
    cells=lambda: pg.locator('.sp-p__cell').count()
    # 1) 처음 60장, 달 사진 수는 그 달 전체
    check(cells()==60,'처음 60장 (%d)'%cells())
    check(pg.locator('.sp-p__month[data-ym="2024-05"] .sp-p__month-count').inner_text().endswith('사진 70'),'5월 사진 수는 처음부터 70')
    check(pg.locator('[data-more] a').count()==1,'끝에 다음 쪽 링크')
    # 2) 내리면 120 → 130, 걸친 달은 한 묶음, 안 겹침
    bottom(pg); pg.wait_for_function("document.querySelectorAll('.sp-p__cell').length===120",timeout=20000)
    check('60장을 더 불러왔어요' in pg.locator('p.sp-vh[role=status]').inner_text(),'화면 읽기 알림: 60장을 더 불러왔어요')
    check(pg.locator('.sp-p__month[data-ym="2024-05"]').count()==1,'5월은 한 묶음')
    check(pg.locator('.sp-p__month[data-ym="2024-05"] .sp-p__cell').count()==70,'5월 칸 70')
    check(overlap(pg,'2024-05')==0,'합친 5월 칸이 안 겹침')
    bottom(pg); pg.wait_for_function("document.querySelectorAll('.sp-p__cell').length===130",timeout=20000)
    check(pg.locator('.sp-p__month').count()==3 and overlap(pg,'2024-04')==0,'달 묶음 3개, 4월 안 겹침')
    pg.wait_for_selector('.sp-more__end'); check('처음 사진까지 모두 봤어요' in pg.locator('.sp-more__end').inner_text() and pg.locator('[data-more] a').count()==0,'끝 줄: 처음 사진까지 모두 봤어요')
    ids=pg.eval_on_selector_all('.sp-p__cell','e=>e.map(x=>x.id)'); check(len(set(ids))==130,'같은 사진 두 번 안 붙음')
    # 3) 크게 보기에서 닫으면 보던 자리로(같은 높이)
    li=pg.locator('.sp-p__cell').nth(100); li.evaluate("e=>e.scrollIntoView({block:'center'})"); pg.wait_for_timeout(200)  # 눌러도 더 스크롤되지 않게 가운데로
    top=li.evaluate("e=>e.getBoundingClientRect().top"); cid=li.get_attribute('id')
    li.locator('a').click(); pg.wait_for_url('**/view/**')
    pg.get_by_role('link',name='닫기').first.click(); pg.wait_for_url('**/home**'); pg.wait_for_timeout(400)
    back=pg.locator('#'+cid)
    check(back.count()==1 and abs(back.evaluate("e=>e.getBoundingClientRect().top")-top)<3,'닫으면 같은 사진이 같은 높이 (%s → %s)'%(round(top),round(back.evaluate("e=>e.getBoundingClientRect().top")) if back.count() else None))
    check(cells()>=120,'돌아오면 그 사진이 든 쪽까지 그려짐 (%d)'%cells())
    # 4) 가족: 링크로 들어와 승인
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gc=b.new_context(viewport={'width':390,'height':844}); gp=gc.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0301'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    # 모아 보기: 60 → 120 → 130, 같은 날 묶음 합침, 제목은 전체 130장
    gp.goto(B+'/album?v=list'); gp.wait_for_timeout(300)
    for btn in ('사진 보기','보기'):
        if gp.get_by_role('button',name=btn,exact=True).count(): gp.get_by_role('button',name=btn,exact=True).click(); gp.wait_for_url('**/album**')
    gcells=lambda: gp.locator('.sp-a__cell').count()
    check(gcells()==60 and '130장' in gp.locator('h1').inner_text(),'가족 모아 보기 처음 60장, 제목 130장 (%d, %s)'%(gcells(),gp.locator('h1').inner_text()))
    POS="(()=>{const o={};for(const e of document.querySelectorAll('.sp-a__cell')){const r=e.getBoundingClientRect();o[e.id]=[Math.round(r.left),Math.round(r.top+scrollY),Math.round(r.height)]}return o})()"
    seam=gp.locator('.sp-a__day').last; seam_n=seam.locator('.sp-a__cell').count()
    before=gp.evaluate(POS)
    bottom(gp); gp.wait_for_function("document.querySelectorAll('.sp-a__cell').length===120",timeout=20000)
    after=gp.evaluate(POS)
    moved=[k for k,v in before.items() if after.get(k)!=v]
    seam_all=gp.locator('.sp-a__day').filter(has_text='5월 15일').locator('.sp-a__cell').count()
    check(0<seam_n<30 and seam_all==30 and not moved,'쪽 경계에 걸친 날(5월 15일 %d장 + 나머지)을 합쳐도 이미 있던 칸이 안 움직임 (합친 뒤 %d장, 움직인 칸 %d)'%(seam_n,seam_all,len(moved)))
    gov=gp.evaluate("""(()=>{let n=0;for(const d of document.querySelectorAll('.sp-a__day')){const r=[...d.querySelectorAll('.sp-a__cell')].map(e=>e.getBoundingClientRect());
      for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i],b=r[j];if(a.left<b.right-1&&b.left<a.right-1&&a.top<b.bottom-1&&b.top<a.bottom-1)n++}}return n})()""")
    check(gov==0,'가족 모아 보기 칸이 겹치지 않음 (%d쌍)'%gov)
    cols=gp.evaluate("(()=>{const d=[...document.querySelectorAll('.sp-a__day')].find(x=>x.querySelectorAll('.sp-a__cell').length>=4);return new Set([...d.querySelectorAll('.sp-a__cell')].map(e=>Math.round(e.getBoundingClientRect().left))).size})()")
    check(cols==2,'휴대폰 2줄 (%d줄)'%cols)
    bottom(gp); gp.wait_for_function("document.querySelectorAll('.sp-a__cell').length===130",timeout=20000)
    days=gp.eval_on_selector_all('.sp-a__day','e=>e.map(x=>x.dataset.day)')
    check(len(days)==len(set(days)),'같은 날 묶음이 두 번 안 나옴 (%d개)'%len(days))
    sums=gp.evaluate("[...document.querySelectorAll('.sp-a__day')].every(d=>d.querySelector('.sp-a__day-count').textContent.trim()===`· ${d.querySelectorAll('.sp-a__cell').length}장`)")
    check(sums,'날짜 묶음 장 수가 칸 수와 같음')
    gp.wait_for_selector('.sp-more__end'); check('처음 사진까지 모두 봤어요' in gp.locator('.sp-more__end').inner_text(),'가족 끝 줄')
    li=gp.locator('.sp-a__cell').nth(110); li.evaluate("e=>e.scrollIntoView({block:'center'})"); gp.wait_for_timeout(200)
    top=li.evaluate("e=>e.getBoundingClientRect().top"); cid=li.get_attribute('id')
    li.locator('a').click(); gp.wait_for_url('**/album/**')
    check('111 / 130' in gp.locator('.sp-v__pos').inner_text(),'크게 보기 자리 111 / 130 (%s)'%gp.locator('.sp-v__pos').inner_text())
    gp.get_by_role('link',name='닫기').first.click(); gp.wait_for_url('**/album**'); gp.wait_for_timeout(400)
    back=gp.locator('#'+cid)
    check(back.count()==1 and abs(back.evaluate("e=>e.getBoundingClientRect().top")-top)<3,'가족도 닫으면 같은 사진이 같은 높이')
    # 넘겨 보기: 옆으로 밀면 카드가 더 붙고 'n / 130'
    gp.goto(B+'/album'); gp.wait_for_timeout(300)
    check(gp.locator('.sp-a__slide').count()==60 and '/ 130' in gp.locator('.sp-a__pos').first.inner_text(),'넘겨 보기 60장, n / 130')
    gp.evaluate("(()=>{const s=document.querySelector('.sp-a__swipe');s.scrollLeft=s.scrollWidth})()")
    gp.wait_for_function("document.querySelectorAll('.sp-a__slide').length===120",timeout=20000)
    check(gp.locator('.sp-a__slide').nth(60).locator('.sp-a__pos-n').inner_text()=='61','붙은 카드 번호가 이어짐(61)')
    # 붙은 카드(70번째)에서 하트를 보내도 그 카드로 돌아옴(스크립트 없는 폼 → to=)
    s70=gp.locator('.sp-a__slide').nth(69); sid70=s70.get_attribute('id')
    s70.evaluate("e=>e.scrollIntoView({inline:'center',block:'nearest'})"); gp.wait_for_timeout(400)
    s70.locator('.sp-a__slide-react button[value="heart:on"]').first.click(); gp.wait_for_url('**to=**'); gp.wait_for_timeout(600)
    check(gp.evaluate(f"(()=>{{const s=document.querySelector('.sp-a__swipe'),e=document.getElementById('{sid70}');if(!e)return false;const a=s.getBoundingClientRect(),r=e.getBoundingClientRect();return r.left<a.right&&r.right>a.left}})()"),'붙은 카드에서 하트 보내도 그 카드로')
    # 넘겨 보기에서 크게 보기 → 닫으면 그 카드
    sid=gp.locator('.sp-a__slide').nth(90).get_attribute('id')[2:]
    gp.goto(B+'/album/'+sid); gp.get_by_role('link',name='닫기').first.click(); gp.wait_for_url('**/album**'); gp.wait_for_timeout(600)
    check(gp.evaluate(f"(()=>{{const s=document.querySelector('.sp-a__swipe'),e=document.getElementById('p-{sid}');if(!e)return false;const a=s.getBoundingClientRect(),r=e.getBoundingClientRect();return r.left<a.right&&r.right>a.left}})()"),'넘겨 보기에서 닫으면 그 카드가 보임')
    gc.close()
    # 5) 스크립트 없으면 '사진 더 보기' 링크로 다음 60장
    saved=c.cookies(); nc=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nc.add_cookies(saved); np_=nc.new_page()
    np_.goto(B+'/home'); check(np_.locator('.sp-p__cell').count()==60 and np_.get_by_role('link',name='사진 더 보기').count()==1,'스크립트 없음: 60장 + 사진 더 보기')
    np_.get_by_role('link',name='사진 더 보기').click(); np_.wait_for_url('**before=**')
    check(np_.locator('.sp-p__cell').count()==60,'다음 쪽 60장')
    np_.get_by_role('link',name='사진 더 보기').click(); np_.wait_for_url('**before=**')
    check(np_.locator('.sp-p__cell').count()==10 and np_.locator('.sp-more__end').count()==1,'마지막 쪽 10장 + 끝 줄')
    nc.close(); c.close()
    b.close()
print('FAILS',FAILS)
