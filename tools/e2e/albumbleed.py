# 앨범 위 고정 머리 + 사진 좌우 꽉(103, 디자인 ParentHomeBleed): 폰은 '앨범' 머리가 스크롤해도 위에 붙고 사진은 화면 끝까지(간격 2px·모서리 0),
# 머리 작은 줄에 사진·영상 수, 아이를 고르면 숨김. PC 폭은 예전 그대로 (mock, 인자: 스크린샷 폴더 엔진)
import os,sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    ctx=br.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    check(not pg.locator('.sp-p__albumhead-sub').is_visible(),'사진 없으면 작은 줄 없음(빈 줄은 숨김)')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f for f in ['u0.jpg','u1.jpg','u2.jpg','u0.jpg','u1.jpg','u2.jpg']])
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__cell-img')
    check('일' in pg.locator('.sp-p__albumhead-sub').inner_text(),'칸 단계 작은 줄은 찍은 날(98c)')
    g=pg.evaluate("(()=>{const r=[...document.querySelectorAll('.sp-p__cell')].map(c=>c.getBoundingClientRect());return [Math.min(...r.map(x=>x.left)),Math.max(...r.map(x=>x.right)),getComputedStyle(document.querySelector('.sp-p__cell')).borderTopLeftRadius,getComputedStyle(document.querySelector('.sp-p__grid')).columnGap]})()")
    check(abs(g[0])<0.5 and abs(g[1]-390)<0.5,f'사진이 화면 끝까지 {g[:2]}')
    check(g[2]=='0px' and g[3]=='2px',f'모서리 0·간격 2px {g[2:]}')
    check(pg.locator('.sp-p__month h2.sp-vh').count()>0,'달 제목은 화면 읽기용만(위 날짜 줄과 겹쳐 뺌, 98e)')
    pg.screenshot(path=W+'/bleed-top.png')
    pg.mouse.wheel(0,500); pg.wait_for_timeout(400)
    h=pg.locator('.sp-p__albumhead').bounding_box(); ttl=pg.get_by_role('heading',name='앨범',level=1)
    check(abs(h['y'])<0.5 and ttl.is_visible(),f'스크롤해도 머리가 위에 붙음 {h["y"]}')
    hit=pg.evaluate("(()=>{const r=document.querySelector('.sp-p__albumhead .sp-p__title').getBoundingClientRect();return document.elementFromPoint(r.left+10,r.top+r.height/2).closest('.sp-p__albumhead')!==null})()")
    check(hit,'머리가 사진 위에 그려짐')
    pg.screenshot(path=W+'/bleed-scroll.png')
    # 키보드로 위로 올라가도 고른 칸이 머리 밑에 숨지 않음(웹킷은 기본 Tab이 링크를 건너뛰어 크롬에서만)
    if eng!='chromium': print('SKIP 키보드 이동(웹킷)')
    else:
     pg.locator('.sp-p__cell-link').last.focus(); hid=[]
     for _ in range(5):
        pg.keyboard.press('Shift+Tab'); pg.wait_for_timeout(250)
        hid.append(pg.evaluate("(()=>{const a=document.activeElement;if(!a.classList.contains('sp-p__cell-link'))return 0;return document.querySelector('.sp-p__albumhead').getBoundingClientRect().bottom-a.getBoundingClientRect().top})()"))
     check(all(x<=0.5 for x in hid),f'키보드로 올라가도 칸이 머리에 안 가려짐 {hid}')
    # 작은 줄 뒤는 사진이 비쳐도 화면색 그대로(대비)
    bg=pg.evaluate("(()=>{const h=document.querySelector('.sp-p__albumhead'),s=document.querySelector('.sp-p__albumhead-sub');return [s.getBoundingClientRect().bottom-h.getBoundingClientRect().top,h.getBoundingClientRect().height-parseFloat(getComputedStyle(h).paddingBottom)]})()")
    check(bg[0]<=bg[1]+0.5,f'작은 줄은 불투명한 자리 안 {bg}')
    # 태블릿 폭: 머리는 붙지만 사진은 예전 모서리·간격(가운데 띠가 잘려 보이지 않게)
    pg.set_viewport_size({'width':800,'height':1100}); pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__cell-img')
    tb=pg.evaluate("[getComputedStyle(document.querySelector('.sp-p__albumhead')).position,getComputedStyle(document.querySelector('.sp-p__cell')).borderTopLeftRadius,getComputedStyle(document.querySelector('.sp-p__grid')).columnGap]")
    check(tb==['sticky','12px','4px'],f'태블릿은 머리만 붙음 {tb}')
    # PC 폭: 예전 그대로(붙지 않음, 모서리 12px)
    pg.set_viewport_size({'width':1280,'height':900}); pg.goto(B+'/home'); pg.wait_for_selector('.sp-p__cell-img')
    pc=pg.evaluate("[getComputedStyle(document.querySelector('.sp-p__albumhead')).position,getComputedStyle(document.querySelector('.sp-p__cell')).borderTopLeftRadius,getComputedStyle(document.querySelector('.sp-p__grid')).columnGap]")
    check(pc==['static','12px','4px'],f'PC는 예전 그대로 {pc}')
    br.close()
print('FAILS',fails)
