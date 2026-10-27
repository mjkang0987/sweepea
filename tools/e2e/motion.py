# 움직임: 레이어 나타남(배경·상자·반짝), 반응 이모지 처음 두 번 + 6초마다 1분 다시, 동작 줄이기면 없음

from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
anims="sel=>[...document.querySelectorAll(sel)].flatMap(e=>e.getAnimations().map(a=>a.animationName+':'+a.effect.getTiming().iterations))"
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','큰이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    # 엄빠 홈: 들어오기 신청 레이어
    pg.goto(B+'/home')
    pg.wait_for_selector('.sp-layer__box',timeout=5000)
    a=pg.evaluate(anims,'.sp-layer__scrim, .sp-layer__box, .sp-layer__emoji')
    check('sp-layer-fade:1' in a and 'sp-layer-pop:1' in a and 'sp-layer-twinkle:2' in a,f'레이어 움직임 {a}')
    pg.wait_for_timeout(500); pg.screenshot(path=S+'motion-layer.png')
    check(pg.locator('.sp-layer__box').evaluate('e=>getComputedStyle(e).opacity')=='1','움직임 끝나면 상자 다 보임')
    # 크게 보기 반응 이모지
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.goto(B+'/home'); pg.get_by_role('button',name='나중에').click() if pg.get_by_role('button',name='나중에').count() else None
    pg.goto(B+'/home'); pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    a=pg.evaluate(anims,'.sp-r__icon')
    check(sorted(a)==sorted(['sp-beat:1','sp-nod:1','sp-bob:1','sp-wobble:1','sp-twinkle:1']),f'크게 보기: 이모지 한 번씩 {a}')
    # 동작 줄이기
    rm=b.new_context(viewport={'width':390,'height':844},reduced_motion='reduce'); rm.add_cookies(ctx.cookies()); r=rm.new_page()
    r.goto(pg.url); check(r.evaluate(anims,'.sp-r__icon')==[],'동작 줄이기: 이모지 멈춤')
    r.goto(B+'/home'); 
    if r.locator('.sp-layer__box').count(): check(r.evaluate(anims,'.sp-layer__scrim, .sp-layer__box, .sp-layer__emoji')==[],'동작 줄이기: 레이어 바로 보임')
print('FAILS',fails)
