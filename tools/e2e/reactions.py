# 부모 최근 반응: 가족 하트·한마디 → 새 반응 수 → 목록 → 읽음
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, "/home/claude/sweepea/tools/e2e"); import layerfix  # noqa
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    check(pg.get_by_role('link',name='알림',exact=True).count()==1,'아래 알림 탭(새 반응 없음)')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_url('**#link')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    h=b.new_context(viewport={'width':390,'height':844}); hp=h.new_page(); hp.goto(B+'/i/'+code)
    hp.fill('#who-name','큰이모'); hp.get_by_role('button',name='들어가기').click(); hp.wait_for_url('**/password**'); hp.fill('#pw','0917'); hp.get_by_role('button',name='들어가기').click(); hp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_url('**done=member-active**')
    gp.goto(B+'/album'); gp.locator('.sp-a__slide').first.locator('.sp-a__slide-react .sp-r__btn').first.click(); gp.wait_for_load_state()
    gp.locator('.sp-a__card-link').first.click(); gp.wait_for_load_state(); gp.fill('#say-body','아이고 많이 컸네'); gp.get_by_role('button',name='보내기').click(); gp.wait_for_load_state()
    pg.goto(B+'/home'); check(pg.get_by_role('link',name='알림, 새 반응 2개').count()==1,'알림 탭 새 반응 2')
    al=pg.locator('.sp-p__alert'); check(al.count()==1 and '큰이모가 가족 앨범에 들어오려고 해요' in al.inner_text() and al.get_attribute('href')=='/settings/family','승인 대기는 앨범 위 띠')
    pg.screenshot(path=D+'r-0.png')
    pg.get_by_role('link',name='알림, 새 반응 2개').click(); pg.wait_for_url('**/reactions')
    t=pg.locator('main').inner_text()
    check('새 반응 · 2' in t and '외할머니 하트를 보냈어요' in t and '외할머니 "아이고 많이 컸네"' in t,'반응·한마디 목록')
    check('들어오려고' not in t,'최근 반응엔 반응만')
    pg.screenshot(path=D+'r-1.png',full_page=True)
    pg.locator('a[href^="/view/"]').first.click(); pg.wait_for_url('**/view/**'); check('아이고 많이 컸네' in pg.locator('.sp-v__talk').inner_text(),'알림 → 크게 보기, 최근 한마디 보임')
    pg.goto(B+'/home'); check(pg.get_by_role('link',name='알림',exact=True).count()==1 and pg.locator('a[href="/reactions"] .sp-p__tab-badge').count()==0,'열고 나면 배지 없음')
    pg.goto(B+'/reactions'); t=pg.locator('main').inner_text(); check('지난 반응' in t and '새 반응' not in t,'다시 열면 지난 반응')
    b.close()
print('ALL OK')
