# 승인 대기 화면에 받은 사진(99): 엄빠가 올리며 만든 링크로 새 이름 → 대기 화면에 그 링크 사진만(다른 사진 안 보임),
# 아래 '다시 확인하기' 고정. 사진 없는 링크(가족 기본 링크)로 들어온 대기는 사진 칸 없이 글만 바뀜. 승인 전 앨범은 대기로 (mock)
import os,sys,random
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def up(pg,files):
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f for f in files])
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    mom=br.new_context(viewport={'width':390,'height':844}).new_page()
    mom.goto(B+'/login'); mom.get_by_role('link',name='개발용으로 계속하기').click(); mom.wait_for_url('**/setup')
    mom.fill('#child','하린'); mom.fill('#birth','2025-01-03'); mom.get_by_role('button',name='다음').click(); mom.wait_for_url('**/setup/password**')
    mom.fill('#pw','0917'); mom.get_by_role('button',name='시작하기').click(); mom.wait_for_url('**/home')
    # 먼저 한 장은 '올리기만'(링크 없음), 그다음 두 장은 링크 만들기
    up(mom,['u0.jpg']); mom.get_by_role('button',name='보내지 않고 올리기만').click(); mom.wait_for_url('**/home**',timeout=60000)
    up(mom,['u1.jpg','u2.jpg']); mom.locator('#up-actions button').first.click()
    mom.wait_for_function("[...document.querySelectorAll('a,input,output,p')].some(e=>/\\/i\\/[A-Za-z0-9]{8}/.test(e.href||e.value||e.textContent))",timeout=60000)
    code=mom.evaluate("(()=>{for(const e of document.querySelectorAll('a,input,output,p')){const m=/\\/i\\/([A-Za-z0-9]{8})/.exec(e.href||e.value||e.textContent);if(m)return m[1]}})()")
    check(bool(code),f'올린 사진으로 링크 만듦 ({code})')
    # 새 이름으로 들어오면 승인 대기 + 받은 사진 2장만
    g=br.new_context(viewport={'width':390,'height':844}).new_page()
    g.goto(B+'/i/'+code); name='큰이모'+str(random.randint(10,99))
    g.fill('#who-name',name); g.keyboard.press('Enter'); g.wait_for_url('**/password**')
    g.fill('#pw','0917'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/wait'); g.wait_for_timeout(600)
    check(g.get_by_role('heading',name='받은 사진').is_visible(),'대기 화면에 받은 사진 제목')
    imgs=g.locator('.sp-f__got-media')
    check(imgs.count()==2,f'링크 사진 2장만(먼저 올린 1장은 안 보임) ({imgs.count()})')
    check('그동안 받은 사진은 여기서 볼 수 있어요' in g.content(),'안내 글: 받은 사진 볼 수 있음')
    ok=g.evaluate("Promise.all([...document.querySelectorAll('img.sp-f__got-media')].map(i=>i.decode().then(()=>i.naturalWidth>0,()=>false)))")
    check(all(ok) and len(ok)==2,f'사진이 열림 {ok}')
    ratio=g.evaluate("[...document.querySelectorAll('img.sp-f__got-media')].map(i=>Math.abs(i.clientWidth/i.clientHeight-i.naturalWidth/i.naturalHeight)<0.02)")
    check(all(ratio),f'사진은 원래 비율 그대로 {ratio}')
    check(all(a for a in g.locator('img.sp-f__got-media').evaluate_all("l=>l.map(i=>i.alt)")),'사진마다 대체 글')
    bar=g.locator('.sp-f__bottom').bounding_box()
    check(bar and abs(bar['y']+bar['height']-844)<=2,'다시 확인하기 막대가 화면 아래 고정')
    g.evaluate("window.scrollTo(0,document.documentElement.scrollHeight)")
    last=g.locator('.sp-f__got-item').last.bounding_box(); bar=g.locator('.sp-f__bottom').bounding_box()
    check(last['y']+last['height']<=bar['y']+1,'마지막 사진이 막대 밑에 안 숨음')
    check(g.locator('.sp-f__got a, .sp-f__got button').count()==0,'누르기·반응 없음')
    g.screenshot(path=W+'/wait-photos.png',full_page=False)
    g.goto(B+'/album'); check(g.url.endswith('/wait'),'승인 전 앨범은 대기 화면으로')
    # 사진 없는 기본 링크(Harin001)로 들어온 대기: 사진 칸 없음, 글 바뀜
    h=br.new_context(viewport={'width':390,'height':844}).new_page()
    h.goto(B+'/i/Harin001'); h.fill('#who-name','작은이모'+str(random.randint(10,99))); h.keyboard.press('Enter'); h.wait_for_url('**/password**')
    h.fill('#pw','1234'); h.get_by_role('button',name='들어가기').click(); h.wait_for_url('**/wait'); h.wait_for_timeout(400)
    check(h.locator('.sp-f__got').count()==0,'빈 묶음: 사진 칸 없음')
    check('그때 사진을 볼 수 있어요' in h.content(),'빈 묶음: 안내 글')
    check(h.locator('.sp-f__bottom--fixed').count()==0,'빈 묶음: 버튼은 제자리(예전 그대로)')
    br.close()
print('FAILS',fails)
