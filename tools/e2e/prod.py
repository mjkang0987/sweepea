# 실제 Supabase로 핵심 흐름: 부모(이메일 테스트 계정, 쿠키 직접) → 처음 설정 → 링크 → 가족 입장·승인 → 올리기 → 보기·반응 → 아이 탭·배지
import base64, json, time, random, urllib.request
from playwright.sync_api import sync_playwright
import os; B=os.environ.get('B','http://localhost:4321'); D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
env=dict(l.split('=',1) for l in open('/home/claude/sweepea/.dev.vars.supabase').read().split('\n') if '=' in l and not l.startswith('#'))
URL=env['SUPABASE_URL']; ANON=env['SUPABASE_ANON_KEY']
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m, flush=True); c or fails.append(m)
def signup():
    email=f'qa+{int(time.time())}{random.randint(0,999)}@sweepea.co.kr'
    req=urllib.request.Request(URL+'/auth/v1/signup',data=json.dumps({'email':email,'password':'Test-'+str(random.randint(10**8,10**9))}).encode(),headers={'apikey':ANON,'content-type':'application/json'})
    t=json.load(urllib.request.urlopen(req))
    assert t.get('access_token'), t
    return {'access':t['access_token'],'refresh':t['refresh_token'],'expiresAt':t.get('expires_at') or int(time.time())+t['expires_in']}
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page()
    pas=signup()
    ctx.add_cookies([{'name':'sp_parent','value':base64.b64encode(json.dumps(pas,separators=(',',':')).encode()).decode(),'url':B}])
    pg.goto(B+'/home'); check('/setup' in pg.url,'새 부모는 처음 설정으로 ('+pg.url+')')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    check(pg.locator('h1',has_text='앨범').count()==1,'처음 설정 → 앨범')
    pg.goto(B+'/settings/children/new'); pg.fill('#name','도윤'); pg.fill('#birth','2023-03-02'); pg.get_by_role('button',name='추가').click(); pg.wait_for_load_state()
    # 올리기(하린 태그)
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.locator('label',has_text='하린').locator('input[name=child]').check()
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=60000)
    check(pg.locator('.sp-p__cell').count()==1,'올린 사진 1장 보임')
    seg=pg.get_by_role('navigation',name='아이 고르기')
    seg.get_by_role('link',name='도윤').click(); pg.wait_for_url('**k=**'); check(pg.locator('.sp-p__cell').count()==0,'도윤 탭 0장(media_children 필터)')
    pg.get_by_role('navigation',name='아이 고르기').get_by_role('link',name='하린').click(); pg.wait_for_url('**k=**'); check(pg.locator('.sp-p__cell').count()==1,'하린 탭 1장')
    pg.screenshot(path=S+'prod-home.png')
    # 링크 → 가족 입장
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait',timeout=30000)
    check(True,'가족 새 이름 → 승인 기다림')
    pg.goto(B+'/settings'); tab=pg.locator('.sp-p__tabs a[href="/settings"]')
    check(tab.get_attribute('aria-label')=='설정, 승인 기다리는 사람 1명','설정 탭 배지(waiting) 1')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_url('**done=member-active**')
    gp.goto(B+'/album'); gp.wait_for_load_state()
    import re
    check('/album' in gp.url and gp.locator('.sp-a__card, .sp-a__cell, .sp-a__slide').count()>=1,'승인 뒤 가족 앨범에 사진 ('+gp.url+')')
    gp.screenshot(path=S+'prod-family.png')
    if gp.locator('.sp-layer').count():
        check('확인했어요' in gp.locator('.sp-layer').inner_text(),'승인 완료 레이어'); gp.locator('.sp-layer button').first.click(); gp.wait_for_load_state()
    # 반응
    btn=gp.locator('.sp-r__btn').first
    if btn.count():
        btn.click(); gp.wait_for_load_state(); check(True,'반응 누름')
        pg.goto(B+'/home'); check((pg.locator('.sp-p__tabs a[href="/reactions"]').get_attribute('aria-label') or '').startswith('알림, 새 반응'),'부모 알림 배지')
    else: check(False,'반응 버튼 없음')
print('FAILS',fails)
