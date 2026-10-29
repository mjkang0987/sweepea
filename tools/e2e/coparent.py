# 엄마아빠 공동 관리(100): 설정 › 가족 '엄마아빠 · 함께 관리' → 초대 링크 → 받은 사람이 아빠로 로그인 → 같은 앨범 엄빠.
# 상대 내보내기(확인 레이어), 함께 관리 중 탈퇴는 '이 앨범에서 나가기'(가족방 그대로), 쓴 링크는 다시 못 씀 (mock)
import sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; W=sys.argv[1] if len(sys.argv)>1 else '/tmp'; eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def new(br): return br.new_context(viewport={'width':390,'height':844}).new_page()
def toast(pg,t): pg.wait_for_function("t=>[...document.querySelectorAll('.sp-toast,.sp-p__toast,#fam-live')].some(e=>e.textContent.includes(t))",arg=t,timeout=15000)
def invite(pg):
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='아빠 초대하기').click(); toast(pg,'초대 링크를 만들었어요')
    # 링크는 정해 둔 공개 주소(sweepea.co.kr)라 개발 서버 주소로 바꿔 연다
    pg.wait_for_selector('#pinvite-url'); return B+'/join/'+pg.locator('#pinvite-url').input_value().rsplit('/join/',1)[1]
def join(br,url):
    g=new(br); g.goto(url); g.get_by_role('button',name='개발용으로 계속하기').click(); g.wait_for_url('**/home**'); return g
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    mom=new(br)
    mom.goto(B+'/login'); mom.get_by_role('link',name='개발용으로 계속하기').click(); mom.wait_for_url('**/setup')
    mom.fill('#child','하린'); mom.fill('#birth','2025-09-17'); mom.get_by_role('button',name='다음').click(); mom.wait_for_url('**/setup/password**')
    mom.fill('#pw','0917'); mom.get_by_role('button',name='시작하기').click(); mom.wait_for_url('**/home')
    mom.goto(B+'/settings/family'); sec=mom.locator('#parents')
    check(sec.get_by_role('heading',name='엄마아빠 · 함께 관리').is_visible() and '엄마 (나)' in sec.inner_text(),'엄마아빠 칸에 나')
    url=invite(mom); check('/join/' in url,f'초대 링크 {url}')
    check(mom.get_by_role('button',name='주소 복사').is_visible(),'초대 카드에 주소 복사')
    mom.screenshot(path=W+'/cp-invite.png')
    # 아빠가 링크로 들어옴
    g=new(br); g.goto(url)
    check(g.get_by_role('heading',name='하린이 앨범을 함께 관리해요').count()==1 or '함께 관리해요' in g.content(),'초대 받은 화면 제목')
    check(g.locator('input[name=role][value=dad]').is_checked(),'엄마가 초대하면 아빠가 미리 골라짐')
    g.screenshot(path=W+'/cp-join.png')
    g.get_by_role('button',name='개발용으로 계속하기').click(); g.wait_for_url('**/home**')
    check('함께 관리해요' in g.content(),'받으면 홈에 함께 관리 안내')
    g.goto(B+'/settings/family'); t=g.locator('#parents').inner_text()
    check('아빠 (나)' in t and '엄마' in t,'아빠 화면에도 엄마아빠 둘')
    # 쓴 링크는 다시 못 씀
    h=new(br); h.goto(url); check('지났어요' in h.content(),'쓴 링크는 지남'); h.context.close()
    # 엄마 화면: 아빠 줄 + 내보내기, 초대 버튼 없음
    mom.goto(B+'/settings/family'); t=mom.locator('#parents').inner_text()
    check('아빠' in t and mom.get_by_role('button',name='아빠 초대하기').count()==0,'엄마 화면에 아빠, 초대 버튼 없음')
    mom.screenshot(path=W+'/cp-two.png')
    # 아빠가 탈퇴 → 나만 나가기
    g.goto(B+'/settings/account'); check(g.get_by_role('link',name='이 앨범에서 나가기').is_visible(),'함께 관리 중이면 탈퇴 대신 이 앨범에서 나가기')
    g.get_by_role('link',name='이 앨범에서 나가기').click(); g.wait_for_selector('#del[open]')
    check('엄마가 계속 관리해요' in g.locator('#del').inner_text() and g.locator('#del input[type=checkbox]').count()==0,'나가기 레이어(확인 체크 없음)')
    g.screenshot(path=W+'/cp-leave.png')
    g.locator('#del').get_by_role('button',name='나가기').click(); g.wait_for_url('**/goodbye**')
    check('앨범에서 나왔어요' in g.content(),'나가면 작별 화면(가족방 그대로)')
    mom.goto(B+'/home'); check(mom.url.endswith('/home'),'엄마 앨범은 그대로')
    mom.goto(B+'/settings/family'); check(mom.get_by_role('button',name='아빠 초대하기').is_visible(),'나가면 다시 초대할 수 있음')
    # 새 아빠를 엄마가 내보냄
    url2=invite(mom); d=join(br,url2)
    mom.goto(B+'/settings/family'); mom.get_by_role('button',name='내보내기 (아빠)').click(); mom.wait_for_selector('#fam-ask[open]')
    check('함께 관리에서 내보낼까요' in mom.locator('#fam-ask').inner_text(),'내보내기 확인 레이어')
    mom.locator('#fam-ask').get_by_role('button',name='내보내기').click(); toast(mom,'내보냈어요')
    d.goto(B+'/home'); check('/setup' in d.url,'내보낸 아빠는 엄빠 화면 없음(처음 설정으로)')
    br.close()
print('FAILS',fails)
