# 한마디 지우기: 내 것만 '지우기', 한 번 더 확인, 지우면 시트 다시 열림·안내, 남의 것(엄빠라도) 못 지움, 다 지우면 화면 안내
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    pc=b.new_context(viewport={'width':390,'height':844}); pg=pc.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); vid=pg.url.split('/view/')[1].split('?')[0]
    pg.fill('#say-body','엄마 한마디'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할아버지'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할아버지').click(); pg.wait_for_url('**done=member-active**')
    gp.goto(B+'/album/'+vid)
    for t in ['할아버지 첫째','할아버지 둘째']:
        gp.fill('#say-body',t); gp.locator('#say').get_by_role('button',name='보내기').click(); gp.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    gp.locator('.sp-v__talk').click()
    items=gp.locator('.sp-v__sheet-item')
    check(items.count()==3,'시트 3개')
    check(items.nth(0).locator('summary').count()==1 and items.nth(2).locator('summary').count()==0,'내 것만 지우기(엄마 것엔 없음)')
    hs=[items.nth(i).locator('.sp-v__sheet-who').bounding_box()['height'] for i in range(3)]; check(max(hs)-min(hs)<1,f'지우기 있어도 이름 줄 높이 같음 {hs}')
    tg=items.nth(0).locator('summary'); tb=tg.bounding_box(); check(tb['width']>=44 and tb['height']>=44,f'지우기 누를 자리 {tb}')
    ic=items.nth(0).locator('.sp-v__sheet-del-icon').bounding_box(); nm=items.nth(0).locator('.sp-v__sheet-who').bounding_box()
    check(abs((ic['y']+ic['height']/2)-(nm['y']+nm['height']/2))<=1 and abs((ic['x']+ic['width'])-(nm['x']+nm['width']))<=2,f'휴지통은 이름 줄 가운데·오른쪽 끝 {ic} {nm}')
    check(tg.get_attribute('aria-label') is None and '한마디 지우기' in tg.inner_text(),'휴지통 버튼 이름(화면 읽기)')
    check(not items.nth(0).locator('.sp-v__sheet-confirm').is_visible(),'처음엔 확인 숨김')
    tg.click(); check(items.nth(0).get_by_text('이 한마디를 지울까요?').is_visible(),'누르면 한 번 더 확인')
    gp.screenshot(path=S+'del-confirm.png')
    items.nth(0).get_by_role('button',name='지우기').click(); gp.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')"); gp.wait_for_function("document.querySelector('#talk')?.matches(':modal')")
    check('#talk' not in gp.url and 'say=' not in gp.url and 'sp-v__sheet--inline' not in (gp.locator('#talk').get_attribute('class') or ''),f'지운 뒤 시트가 모달로 다시 열림, 주소엔 안내 표시 없음 {gp.url}')
    check(gp.locator('#talk').get_attribute('aria-describedby')=='talk-note','안내를 시트 설명으로 연결(화면 읽기)')
    check(gp.locator('#talk-title').evaluate("e=>getComputedStyle(e).outlineStyle")=='none','다시 열 때 제목에 테두리 없음')
    check(gp.locator('#talk > .sp-toast').filter(has_text='한마디를 지웠어요.').is_visible() and gp.locator('.sp-v__sheet-note').count()==0,'지운 안내는 시트 위 토스트(박스 없음)')
    check(gp.locator('.sp-toast svg, .sp-toast [aria-hidden]').count()==0,'토스트에 아이콘 없음')
    tb=gp.locator('#talk > .sp-toast').bounding_box(); sb=gp.locator('#talk').bounding_box()
    check(tb['y']+tb['height']<=sb['y'] and tb['y']>=0,f'토스트는 시트 위 바깥(한마디 안 가림) {tb} {sb}')
    sv=gp.url
    gp.goto(sv.split('?')[0].split('#')[0]+'?say=deleted'); gp.wait_for_function("document.querySelector('#talk')?.matches(':modal')")
    gp.wait_for_timeout(700); gp.screenshot(path=S+'del-toast.png')
    check(gp.locator('#talk > .sp-toast').count()==1,'새로 열린 페이지(서버 그림)에서도 시트 안 토스트')
    gp.keyboard.press('Escape'); gp.goto(sv); gp.locator('.sp-v__talk').click(); gp.wait_for_function("document.querySelector('#talk').open")
    left=[gp.locator('.sp-v__sheet-item').nth(i).inner_text() for i in range(gp.locator('.sp-v__sheet-item').count())]
    check(len(left)==2 and not any('할아버지 둘째' in x for x in left),f'지운 것 빠짐 {left}')
    check('2' in gp.locator('.sp-v__talk').inner_text(),'한 줄 수도 2')
    gp.screenshot(path=S+'del-after.png')
    gp.get_by_role('link',name='닫기').last.click()
    check(not gp.locator('.sp-v__sheet-item').first.is_visible(),'닫으면 판 안에 펼쳐지지 않고 사라짐')
    gp.reload(); check(gp.get_by_text('한마디를 지웠어요.').count()==0 or not gp.get_by_text('한마디를 지웠어요.').is_visible(),'새로 고침하면 안내 다시 안 뜸')
    # 없는 한마디 지우기 → 실패 안내
    gp.request.post(B+'/album/'+vid,form={'del':'00000000-0000-4000-8000-000000000000','back':'/album/'+vid},max_redirects=0)
    r=gp.request.post(B+'/album/'+vid,form={'del':'00000000-0000-4000-8000-000000000000','back':'/album/'+vid},max_redirects=0)
    loc=r.headers.get('location','')
    gp.goto(B+loc); check('delerror' in loc and gp.get_by_text('지우지 못했어요. 다시 해 주세요.').is_visible(),f'지우기 실패 안내 {loc}')
    # 엄빠는 할아버지 것 못 지움(버튼 없음 + 직접 보내도 막힘)
    pg.goto(B+'/view/'+vid); pg.locator('.sp-v__talk').click()
    pi=pg.locator('.sp-v__sheet-item')
    mine=[pi.nth(i).locator('summary').count() for i in range(pi.count())]
    check(mine.count(1)==1,f'엄빠 화면: 지우기는 엄마 것 하나 {mine}')
    gid=gp.locator('.sp-v__sheet-item button[name=del]').first.get_attribute('value') if gp.locator('.sp-v__sheet-item button[name=del]').count() else None
    r=pg.request.post(B+'/view/'+vid,form={'del':gid,'back':'/view/'+vid},max_redirects=0)
    pg.goto(B+'/view/'+vid); check(pg.locator('.sp-v__sheet-item').count()==2,'엄빠가 할아버지 것 지우려 해도 그대로')
    # 다 지우면 화면 안내
    gp.goto(B+'/album/'+vid); gp.locator('.sp-v__talk').click()
    gp.locator('.sp-v__sheet-item summary').first.click(); gp.locator('.sp-v__sheet-item').get_by_role('button',name='지우기').first.click(); gp.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    pg.goto(B+'/view/'+vid); pg.locator('.sp-v__talk').click(); pg.locator('.sp-v__sheet-item summary').first.click(); pg.locator('.sp-v__sheet-item').get_by_role('button',name='지우기').first.click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    check(pg.locator('.sp-v__talk').count()==0 and pg.get_by_text('한마디를 지웠어요.').is_visible(),'다 지우면 한 줄 없음·화면 안내')
    check('say=' not in pg.url,'다 지운 뒤에도 주소에서 안내 표시 뗌')
    html=pg.request.get(B+'/view/'+vid+'?say=deleted').text(); check("getElementById('talk')" not in html,'남은 한마디 없으면 인라인 스크립트도 없음')
    # 스크립트 없음: #talk 펼침에서도 지우기
    # 스크립트 없음: 지운 뒤 판 안에 펼쳐진 목록과 안내
    pg.fill('#say-body','스크립트 없이 지울 것'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    pg.fill('#say-body','남길 것'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    nj=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nj.add_cookies(pc.cookies()); n=nj.new_page()
    n.goto(B+'/view/'+vid); n.locator('.sp-v__talk').click()
    n.locator('.sp-v__sheet-item').filter(has_text='스크립트 없이 지울 것').locator('summary').click()
    n.locator('.sp-v__sheet-item').filter(has_text='스크립트 없이 지울 것').get_by_role('button',name='지우기').click(); n.wait_for_load_state()
    check(n.get_by_text('한마디를 지웠어요.').is_visible() and n.locator('.sp-v__sheet-item').filter(has_text='남길 것').is_visible(),'스크립트 없어도 지우고 목록·안내 보임')
    check(n.locator('.sp-v__sheet .sp-v__sheet-form').is_hidden(),'스크립트 없을 때 입력칸은 판 것 하나')
print('FAILS',fails)
