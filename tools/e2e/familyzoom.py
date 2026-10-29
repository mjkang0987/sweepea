# 가족 앨범 사진 크기(98a): 모아 보기 −/+ 1·2·3칸 = 사진 전부 → 월별 달 카드(대표 3장, 누르면 그 달부터 3칸).
# 보기(넘겨/모아)와 칸 단계는 그 기기에 기억(달 카드로 들어간 쪽은 빼고) (mock, 인자: 스크린샷 폴더 엔진)
import os,sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
COLS="getComputedStyle(document.querySelector('.sp-a__grid')).gridTemplateColumns.split(' ').length"
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    pg=br.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f for f in ['u0.jpg','u1.jpg','u2.jpg','u0.jpg','u1.jpg','u2.jpg']])
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=br.new_context(viewport={'width':390,'height':844}).new_page(); g.goto(B+'/i/'+code)
    g.fill('#who-name','외할머니'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/password**'); g.fill('#pw','0917'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    g.goto(B+'/album'); g.wait_for_timeout(300)
    for btn in ('사진 보기','보기','닫기'):
        if g.get_by_role('button',name=btn,exact=True).count(): g.get_by_role('button',name=btn,exact=True).first.click(); g.wait_for_load_state()
    check(g.locator('.sp-a__swipe').count()==1,'처음은 넘겨 보기')
    g.get_by_role('link',name='모아 보기').click(); g.wait_for_url('**v=list**'); g.wait_for_selector('.sp-a__cell-img')
    check(g.evaluate(COLS) is not None and g.locator('.sp-a__grid--2').count()>0,'모아 보기 처음 2칸')
    g.get_by_role('link',name='작게(한 줄에 더 많이)').click(); g.wait_for_url('**z=3**'); g.wait_for_selector('.sp-a__cell-img')
    check(g.evaluate(COLS)==3 and g.locator('.sp-a__cell').count()==6,'작게 → 3칸, 사진 전부')
    g.get_by_role('link',name='작게(달마다 대표 사진)').click(); g.wait_for_url('**z=m**'); g.wait_for_selector('.sp-a__mcard')
    cards=g.locator('.sp-a__mcard'); t=cards.first.inner_text().replace('\n',' ')
    check(cards.count()==2 and '4장' in t,f'월별: 달 카드 2장, 장 수 ({cards.count()}, {t})')
    check(cards.first.locator('.sp-a__mcard-img').count()==3,'대표 3장')
    check(g.locator('.sp-a__zoom-btn[aria-disabled=true]').inner_text()=='−','월별이면 작게 꺼짐')
    fs=g.evaluate("parseFloat(getComputedStyle(document.querySelector('.sp-a__mcard-title')).fontSize)"); check(fs>=28,f'달 제목은 어르신 글자 ({fs}px)')
    g.screenshot(path=W+'/fz-m.png')
    g.goto(B+'/album'); g.wait_for_timeout(300)
    check(g.locator('.sp-a__mcard').count()==2,'다시 열면 모아 보기·월별 기억')
    cards.nth(1).click(); g.wait_for_url('**before=**'); g.wait_for_selector('.sp-a__cell-img')
    check('z=3' in g.url and g.evaluate(COLS)==3 and g.locator('.sp-a__cell').count()==2,'달 카드 → 그 달부터 3칸')
    g.locator('.sp-a__cell-link').first.click(); g.wait_for_url('**/album/**')
    g.get_by_role('link',name='닫기').first.click(); g.wait_for_url('**/album?**'); g.wait_for_timeout(300)
    check('z=3' in g.url and g.locator('.sp-a__cell').count()>0,'크게 보기에서 닫으면 보던 3칸으로')
    g.goto(B+'/album'); g.wait_for_timeout(300)
    check(g.locator('.sp-a__mcard').count()==2,'달 카드로 들어간 3칸·크게 보기·닫고 돌아온 쪽은 기억 안 함')
    g.get_by_role('link',name='넘겨 보기').click(); g.wait_for_load_state(); g.goto(B+'/album'); g.wait_for_timeout(300)
    check(g.locator('.sp-a__swipe').count()==1,'넘겨 보기를 고르면 다음에도 넘겨 보기')
    br.close()
print('FAILS',fails)
