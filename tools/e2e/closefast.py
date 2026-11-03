# 닫기 더 빠르게 ②(128): 칸 보기에서 깊은 사진(?to=)·달 카드(?at=)는 그 주변 한 쪽(60장 이하)만 그리고, 위로 올리면 최근 사진을 이어 붙임(보던 칸은 안 움직임)
import os,sys,tempfile,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=tempfile.gettempdir()
import importlib.util
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
# loadmore.py와 같은 사진 130장(6월 30·5월 70·4월 30)
src=open(D+'loadmore.py').read(); ns={'__file__':D+'loadmore.py'}
exec(src[:src.index('FAILS=[]')].replace("W=sys.argv[1] if len(sys.argv)>1 else tempfile.gettempdir()",f"W={W!r}"),ns)
FILES=ns['FILES']
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2024-03-01'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0301'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    for k in range(0,len(FILES),50):
        pg.goto(B+'/upload'); pg.set_input_files('#up-files',FILES[k:k+50]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=300000)
        pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=300000)
    pg.goto(B+'/home?v=list&z=3')
    for _ in range(4): pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); pg.wait_for_timeout(1000)
    pg.wait_for_function("document.querySelectorAll('.sp-p__cell').length===130",timeout=20000)
    ids=pg.eval_on_selector_all('.sp-p__cell','e=>e.map(x=>x.id.slice(2))')
    deep=ids[100]
    # 1) 깊은 사진 닫기: 주변 한 쪽만
    t0=time.time(); pg.goto(B+f'/home?v=list&z=3&to={deep}#c-{deep}'); dt=time.time()-t0
    n=pg.locator('.sp-p__cell').count()
    check(n<=60 and pg.locator(f'#c-{deep}').count()==1,f'깊은 사진(101번째) 닫기: 주변 {n}장만 그림 ({dt:.2f}초)')
    vis=pg.evaluate(f"(()=>{{const r=document.getElementById('c-{deep}').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}})()")
    check(vis,'그 사진 칸이 화면 안')
    check(pg.locator('[data-less] a').count()==1,'위에 최근 사진 더 보기')
    # 2) 그대로 있을 때 보던 칸이 움직이지 않음(위에 붙여도)
    pg.wait_for_timeout(1500)
    top1=pg.evaluate(f"document.getElementById('c-{deep}').getBoundingClientRect().top")
    # 3) 위로 올리면 최근 사진을 이어 붙여 끝까지
    for _ in range(8):
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(900)
        if pg.locator('[data-less]').count()==0: break
    allids=pg.eval_on_selector_all('.sp-p__cell','e=>e.map(x=>x.id.slice(2))')
    check(pg.locator('[data-less]').count()==0 and allids[0]==ids[0],'위로 올리면 최근 사진까지 이어 붙음(맨 위 = 가장 최근)')
    check(len(allids)==len(set(allids)),'같은 사진 두 번 안 붙음')
    check(allids==ids[:len(allids)],'순서 그대로(최근 → 옛날)')
    check(pg.locator('#m-2024-05').count()==1 and pg.locator('#m-2024-06').count()==1,'달 표식은 달마다 하나')
    # 보던 칸 보정: 한 번 붙인 직후 칸 위치(따로)
    pg.goto(B+f'/home?v=list&z=3&to={deep}#c-{deep}'); pg.wait_for_timeout(300)
    a0=pg.evaluate(f"document.getElementById('c-{deep}').getBoundingClientRect().top")
    pg.evaluate("window.scrollBy(0,-1200)"); pg.wait_for_timeout(1500)
    a1=pg.evaluate(f"document.getElementById('c-{deep}').getBoundingClientRect().top")
    print('before/after scroll', a0, a1)
    check(abs((a1-a0)-1200)<5,f'위에 붙여도 보던 칸이 안 튐 ({a0:.0f} → {a1:.0f}, 올린 만큼 1200)')
    # 4) 앞쪽 사진(30번째 안)이면 처음부터 그대로(위 이어 붙이기 없음)
    near=ids[10]; pg.goto(B+f'/home?v=list&z=3&to={near}#c-{near}')
    check(pg.locator('[data-less]').count()==0 and pg.locator('.sp-p__cell').first.get_attribute('id')=='c-'+ids[0],'앞쪽 사진이면 처음부터, 위 이어 붙이기 없음')
    # 5) 달 카드(4월)도 주변만
    pg.goto(B+'/home?v=list&z=3&at=2024-04#m-2024-04')
    check(pg.locator('.sp-p__cell').count()<=60 and pg.locator('#m-2024-04').count()==1 and pg.locator('[data-less] a').count()==1,'4월 카드: 주변 한 쪽 + 4월 표식 + 위 이어 붙이기')
    # 6) 스크립트 없으면 링크로 그 쪽
    saved=c.cookies(); nc=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); nc.add_cookies(saved); np_=nc.new_page()
    np_.goto(B+f'/home?v=list&z=3&to={deep}'); np_.get_by_role('link',name='최근 사진 더 보기').click(); np_.wait_for_url('**after=**')
    check(np_.locator('.sp-p__cell').count()>0,'스크립트 없음: 최근 사진 더 보기 링크로 그 쪽')
    nc.close()
    # 7) 엄빠 넘겨 보기(129): 깊은 카드도 주변만, 'n / 전체'의 n이 맞고 맨 앞으로 밀면 최근 카드가 앞에 붙음(보던 카드 그대로)
    def swipe_check(page,url,prefix,who):
        page.goto(url); page.wait_for_timeout(600)
        n=page.locator('.sp-a__slide').count()
        pos=page.locator(f'#{prefix}{deep} .sp-a__pos-n').inner_text().replace(',','')
        check(n<=60 and pos=='101',f'{who} 넘겨 보기 깊은 카드: 주변 {n}장, 자리 {pos}번째')
        for _ in range(10):
            page.evaluate("document.querySelector('.sp-a__swipe').scrollLeft=0"); page.wait_for_timeout(700)
            if page.locator('[data-less]').count()==0: break
        got=page.eval_on_selector_all('.sp-a__slide','e=>e.map(x=>x.id.slice(2))')
        check(page.locator('[data-less]').count()==0 and got==ids[:len(got)] and len(got)==len(set(got)) and got[0]==ids[0],f'{who} 넘겨 보기: 앞으로 밀면 최근 카드까지 순서대로 붙음 ({len(got)}장)')
        firstpos=page.locator(f'#{prefix}{ids[0]} .sp-a__pos-n').inner_text()
        check(firstpos=='1','붙인 맨 앞 카드는 1번째')
    swipe_check(pg,B+f'/home?v=swipe&to={deep}#c-{deep}','c-','엄빠')
    # 8) 가족 앨범(129): 칸·넘겨 보기 둘 다
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    gc=b.new_context(viewport={'width':390,'height':844}); gp=gc.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할머니'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0301'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+f'/album?v=list&z=3&to={deep}#c-{deep}'); gp.wait_for_timeout(500)
    for sel in ['.sp-layer:not([hidden]) form button']:
        while gp.locator(sel).count(): gp.locator(sel).last.click(); gp.wait_for_load_state(); gp.wait_for_timeout(200)
    gp.goto(B+f'/album?v=list&z=3&to={deep}#c-{deep}'); gp.wait_for_timeout(500)
    n=gp.locator('.sp-a__cell').count()
    check(n<=60 and gp.locator(f'#c-{deep}').count()==1 and gp.locator('[data-less] a').count()==1,f'가족 칸 보기 깊은 사진: 주변 {n}장 + 위 이어 붙이기')
    for _ in range(8):
        gp.evaluate("window.scrollTo(0,0)"); gp.wait_for_timeout(900)
        if gp.locator('[data-less]').count()==0: break
    got=gp.eval_on_selector_all('.sp-a__day[data-day="all"] .sp-a__cell','e=>e.map(x=>x.id.slice(2))')
    check(gp.locator('[data-less]').count()==0 and got==ids[:len(got)] and len(got)==len(set(got)) and got[0]==ids[0],f'가족 칸 보기: 위로 올리면 최근 사진까지 순서대로 ({len(got)}장)')
    swipe_check(gp,B+f'/album?v=swipe&to={deep}#p-{deep}','p-','가족')
    gp.screenshot(path='/home/user/sweepea/tools/shots/family-swipe-close.png')
    # 9) 132: 방금 올라온 안 본 사진(엄빠가 2장 더 올림)이 있을 때 깊은 사진에서 닫아도 번호·순서가 맞음, 맨 위 묶음 없이 제자리에 '신규'
    gp.goto(B+'/album?v=list&z=3'); check(gp.locator('.sp-f__lead').filter(has_text='올라왔어요').count()==1,'가족 맨 위 쪽: 최근 날짜 안내 있음')
    gp.goto(B+f'/album?v=list&z=3&to={deep}#c-{deep}'); check(gp.locator('.sp-f__lead').filter(has_text='올라왔어요').count()==0,'가족 주변만 그린 쪽: 최근 날짜 안내 없음(깊은 사진 날짜를 최근으로 안 보임)')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    gp.goto(B+'/album?v=list&z=3')
    check(gp.locator('.sp-a__day[data-day="new"] .sp-a__cell').count()==2,'맨 위 쪽: 방금 올라온 2장은 묶음에')
    new2=gp.eval_on_selector_all('.sp-a__day[data-day="new"] .sp-a__cell','e=>e.map(x=>x.id.slice(2))')
    gp.goto(B+f'/album?v=swipe&to={deep}#p-{deep}'); gp.wait_for_timeout(600)
    pos=gp.locator(f'#p-{deep} .sp-a__pos-n').inner_text().replace(',','')
    check(pos=='103' and all(gp.locator(f'#p-{x}').count()==0 for x in new2),f'가족 넘겨 보기: 방금 올라온 사진이 있어도 깊은 카드 자리 맞음 ({pos}, 묶음 없음)')
    for _ in range(10):
        gp.evaluate("document.querySelector('.sp-a__swipe').scrollLeft=0"); gp.wait_for_timeout(700)
        if gp.locator('[data-less]').count()==0: break
    got=gp.eval_on_selector_all('.sp-a__slide','e=>e.map(x=>x.id.slice(2))')
    check(len(got)==132 and set(got[:2])==set(new2) and got[2:]==ids and len(set(got))==132,'앞으로 밀면 132장 순서대로(방금 올라온 2장이 맨 앞)')
    nums=gp.eval_on_selector_all('.sp-a__slide .sp-a__pos-n','e=>e.map(x=>x.textContent.trim())')
    check(nums==[str(i+1) for i in range(len(nums))],'카드 번호 1부터 끊김 없이')
    check(all(gp.locator(f'#p-{x} .sp-a__new').count()>0 for x in new2),'방금 올라온 2장은 제자리에서 신규 표시')
    gc.close()
    b.close()
print('FAILS',FAILS)
