# PC 화면: 넓은 화면에서 넓게·칸 수, 좁은 화면 그대로, 올리기 끌어다 놓기
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':1280,'height':800}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload')
    side=pg.locator('.sp-p__up-side').bounding_box(); main=pg.locator('.sp-p__up-main').bounding_box()
    check(side['x']>main['x']+main['width']-1,'올리기 두 칸(오른쪽에 아이·그룹)')
    # 끌어다 놓기
    pg.evaluate("""async()=>{const r=await fetch('/icons/icon-512.png');const f=new File([await r.blob()],'a.png',{type:'image/png'});
      const dt=new DataTransfer();dt.items.add(f);const pick=document.getElementById('up-pick');
      pick.dispatchEvent(new DragEvent('dragover',{dataTransfer:dt,bubbles:true,cancelable:true}));
      pick.dispatchEvent(new DragEvent('drop',{dataTransfer:dt,bubbles:true,cancelable:true}));}""")
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    check(pg.locator('#up-grid li').count()==1,'끌어다 놓아 고름'); pg.screenshot(path=D+'pc-3.png')
    pg.get_by_role('button',name='올리고 카톡으로 보내기').click(); pg.wait_for_selector('#up-done:not([hidden])',timeout=30000)
    check(not pg.locator('#up-form').is_visible(),'PC에서도 다 올리면 올리기 칸은 숨김')
    pg.goto(B+'/home')
    tabs=pg.locator('.sp-p__tabs').bounding_box(); check(tabs['y']<5,'PC 부모 메뉴는 위')
    cols=pg.evaluate("getComputedStyle(document.querySelector('.sp-p__grid')).gridTemplateColumns.split(' ').length"); check(cols==6,'부모 앨범 6칸')
    check(pg.locator('main').bounding_box()['width']>1000,'부모 앨범 넓게'); pg.screenshot(path=D+'pc-2.png')
    pg.goto(B+'/settings'); check(pg.locator('main').bounding_box()['width']<600,'설정은 좁게 그대로')
    # 가족
    g=b.new_context(viewport={'width':1280,'height':800}); gp=g.new_page(); gp.goto(B+'/i/Harin001')
    gp.get_by_role('button',name='이모',exact=True).click(); gp.wait_for_url('**/password**'); gp.fill('#pw','1234'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/album')
    check(gp.locator('main').bounding_box()['width']<600,'넘겨 보기는 좁게 그대로')
    gp.goto(B+'/album?v=list'); check(gp.locator('main').bounding_box()['width']>900,'모아 보기는 넓게')
    check(gp.evaluate("getComputedStyle(document.querySelector('.sp-a__grid--2')).columnCount")=='4','모아 보기 4줄')
    gp.screenshot(path=D+'pc-1.png')
    gp.locator('.sp-a__cell-link').first.click(); gp.wait_for_load_state(); gp.screenshot(path=D+'pc-4.png')
    m=b.new_context(viewport={'width':390,'height':844}); mp=m.new_page(); mp.goto(B+'/settings')
    b.close()
print('ALL OK')
