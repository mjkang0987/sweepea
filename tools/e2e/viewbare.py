# 크게 보기 사진만(84, 대기열 C): 사진을 한 번 누르면 위 메뉴·아래 판·화살표가 사라지고 검은 바탕, 다시 누르면 돌아옴.
# 넘겨도 유지, 키보드(포커스하면 보이는 버튼·Esc), 영상은 멈춘 상태에서만 전환 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
bare="'bare' in document.querySelector('.sp-v').dataset"
shown="['.sp-v__bar','.sp-v__dock','a[rel=next]'].map(s=>{const e=document.querySelector(s);return !!e&&e.checkVisibility()})"
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={'width':390,'height':844})
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg',D+'v.mp4']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    ids=[h.split('/view/')[1] for h in pg.locator('.sp-p__cell-link').evaluate_all('e=>e.map(a=>a.getAttribute("href"))')]
    vids=[]; photos=[]
    for i in ids:
        pg.goto(B+'/view/'+i); pg.wait_for_selector('.sp-v')
        (vids if pg.locator('video').count() else photos).append(i)
    # 1) 사진: 누르면 사진만
    pg.goto(B+'/view/'+photos[0]); pg.wait_for_selector('.sp-v__track')
    check(pg.evaluate(shown)==[True,True,True] and not pg.evaluate(bare),'처음엔 메뉴·판·화살표 보임')
    pg.mouse.click(195,420)
    check(pg.evaluate(bare) and pg.evaluate(shown)==[False,False,False],'사진을 누르면 메뉴·판·화살표 숨김')
    check(pg.evaluate("getComputedStyle(document.querySelector('.sp-v')).backgroundColor")=='rgb(0, 0, 0)','바탕은 검정')
    check(pg.locator('.sp-v__ui').inner_text()=='메뉴 보이기','버튼 이름이 메뉴 보이기로')
    pg.screenshot(path=D+'../shots/viewbare.png') if os.path.isdir(D+'../shots') else None
    # 2) 넘겨도 사진만 유지
    # 지금 사진 옆의 사진(영상이면 그 화면을 새로 여니 사진인 칸으로)
    k,nid=pg.evaluate("(()=>{const w=JSON.parse(document.querySelector('.sp-v').dataset.slides),at=w.slides.findIndex(x=>x.id===document.querySelector('.sp-v').dataset.id);const k=w.slides.findIndex((x,i)=>i>at&&!x.video);return [k,w.slides[k].id]})()")
    pos0=pg.locator('.sp-v__pos').inner_text()
    pg.evaluate("window.__same=1")
    pg.locator('.sp-v__track').evaluate(f't=>t.scrollTo({{left:{k}*t.clientWidth}})')
    pg.wait_for_url('**/view/'+nid+'**'); pg.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()!=='"+pos0+"'")
    check(pg.evaluate('window.__same')==1,'넘기기는 페이지 다시 안 부름')
    check(pg.evaluate(bare) and pg.evaluate(shown)[:2]==[False,False],'넘겨도 사진만 유지')
    # 3) 다시 누르면 돌아옴(판은 넘긴 사진 것)
    pg.mouse.click(195,420)
    check(not pg.evaluate(bare) and pg.evaluate(shown)[:2]==[True,True],'다시 누르면 돌아옴')
    check(pg.locator('.sp-v__pos').inner_text()!=pos0,'위 메뉴는 넘긴 사진 기준')
    # 4) 키보드: 포커스하면 보이는 버튼, Enter로 숨기고 Esc로 돌아옴
    ui=pg.locator('.sp-v__ui'); ui.focus(); pg.keyboard.press('Shift+Tab'); pg.keyboard.press('Tab')
    box=ui.bounding_box()
    arrow=pg.locator('a[rel=next]').bounding_box()['height']
    check(box and box['width']>40 and box['height']>=arrow-0.5,'키보드 포커스하면 버튼이 보임(화살표만큼 큼) '+str(box))
    pg.keyboard.press('Enter')
    check(pg.evaluate(bare),'Enter로 사진만')
    pg.keyboard.press('Escape')
    check(not pg.evaluate(bare) and ui.inner_text()=='메뉴 숨기기','Esc로 돌아옴')
    # 7) 영상: 멈춘 상태에서 누르면 사진만(재생 버튼도 숨김), 재생 중엔 누르면 일시정지
    pg.goto(B+'/view/'+vids[0]); pg.wait_for_selector('.sp-v__play:not([hidden])')
    pg.mouse.click(195,300)
    check(pg.evaluate(bare) and pg.locator('.sp-v__play').is_hidden() and pg.locator('.sp-v__ctrl').is_hidden(),'영상 멈춤: 누르면 재생 버튼·막대까지 숨김')
    pg.mouse.click(195,300)
    check(not pg.evaluate(bare) and pg.locator('.sp-v__play').is_visible(),'다시 누르면 돌아옴')
    pg.locator('.sp-v__play').click(); pg.wait_for_function("'playing' in document.querySelector('.sp-v').dataset",timeout=5000)
    pg.mouse.click(195,300); pg.wait_for_function("document.querySelector('video').paused",timeout=5000)
    check(not pg.evaluate(bare),'재생 중 누르면 일시정지만(사진만 아님)')
    b.close()
print('FAILS',FAILS)
