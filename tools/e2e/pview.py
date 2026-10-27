# 엄빠 크게 보기: 앨범 → 크게 보기, 반응·한마디(부모 계정), 수정 버튼, 넘기기, 가족 화면에 부모 하트가 셈
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    vid=pg.url.split('/view/')[1].split('?')[0]
    check(pg.locator('.sp-v__pos').inner_text()=='1 / 3','1 / 3')
    check(pg.get_by_role('link',name='닫기').get_attribute('href')=='/home','닫기 → 앨범')
    check(pg.get_by_role('link',name='저장').count()==1,'엄빠는 늘 저장')
    ed=pg.get_by_role('link',name='사진 정보 수정')
    check(ed.get_attribute('href')=='/photo/'+vid,'수정 버튼 → 사진 정보')
    eb=ed.bounding_box(); pb=pg.locator('.sp-v__panel').bounding_box()
    check(eb['y']+eb['height']<=pb['y']+1 and eb['x']+eb['width']>300,'수정 버튼이 판 바로 위 오른쪽')
    pg.screenshot(path=S+'pview.png')
    pg.get_by_role('button',name='하트 0개').click(); pg.wait_for_load_state()
    check(pg.get_by_role('button',name='하트 1개').get_attribute('aria-pressed')=='true','엄빠 하트 켜짐')
    check('/view/'+vid in pg.url,'반응 뒤 같은 화면')
    pg.fill('.sp-say .sp-f__input','우리 딸 최고'); pg.get_by_role('button',name='보내기').click(); pg.wait_for_selector('.sp-toast')
    check(pg.get_by_text('보냈어요. 가족도 볼 수 있어요.').count()==1,'한마디 보냄 안내')
    check('우리 딸 최고' in pg.locator('.sp-v__talk').inner_text(),'최근 한마디 한 줄(판 안)')
    pg.screenshot(path=S+'pview-say.png')
    pg.get_by_role('link',name='다음 사진').click(); pg.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='2 / 3'")
    check(pg.locator('.sp-v__pos').inner_text()=='2 / 3','다음 → 2 / 3')
    # 가족이 보면 부모 하트도 셈
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','큰이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 큰이모').click(); pg.wait_for_url('**done=member-active**')
    gp.goto(B+'/album/'+vid); gp.wait_for_load_state()
    check(gp.get_by_role('button',name='하트 1개').get_attribute('aria-pressed')=='false','가족 화면: 엄빠 하트 1개(내 것 아님)')
    check(gp.locator('.sp-v__edit').count()==0,'가족 화면엔 수정 버튼 없음')
    gp.screenshot(path=S+'gview.png')
    # 엄빠 알림에 내 반응은 없음
    pg.goto(B+'/home'); check(pg.locator('.sp-p__tabs a[href="/reactions"] .sp-p__tab-badge').count()==0,'내 반응은 알림 배지에 안 셈')
    # 큰 글씨·가로 화면에서도 버튼끼리 안 가림(리뷰 1회차)
    ctx=pg.context
    probe="""()=>{const out={};for(const s of ['.sp-v__edit','.sp-v__arrow--next','.sp-v__arrow--prev','.sp-v__bar a:last-child','.sp-v__bar a']){const e=document.querySelector(s);if(!e||e.hidden)continue;const b=e.getBoundingClientRect();
      let bad=0,n=0;for(const [fx,fy] of [[.5,.5],[.3,.5],[.7,.5],[.5,.3],[.5,.7]]){n++;const h=document.elementFromPoint(b.left+b.width*fx,b.top+b.height*fy);if(!h||!e.contains(h))bad++}
      out[s]=Math.round(100*bad/n)}return out}"""
    # 엄빠는 기본 글씨(가족 글씨 쿠키는 가족 기기에만). 큰 글씨는 같은 휴대폰을 가족도 쓸 때
    for size in ['base','large','xlarge']:
        ctx.add_cookies([{'name':'sp_size','value':size,'url':B}])
        for vp in [(390,844),(375,667),(844,390)]:
            pg.set_viewport_size({'width':vp[0],'height':vp[1]}); pg.goto(B+'/view/'+vid); r=pg.evaluate(probe)
            worst=max(r.values()) if r else 100
            check(worst<=5 and '.sp-v__edit' in r,f'{size} {vp} 가림 {r}')
print('FAILS',fails)
