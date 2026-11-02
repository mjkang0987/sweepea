# 신규 배지(사용자 2026-11-02 "신규 사진 확인하고 닫기 누르면 신규 배지 안 없어짐"): 가족이 신규 사진을 크게 보고 닫으면 배지가 빠져야 한다
import layerfix
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/user/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','이모'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 이모').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+'/album')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    gp.goto(B+'/album'); n0=gp.locator('.sp-a__new:not(.sp-a__new--event)').count()
    check(n0==2,f'가족 앨범 신규 2장 ({n0})')
    gp.locator('.sp-a__card-link').first.click(); gp.wait_for_url('**/album/**'); gp.wait_for_timeout(500)
    seen=gp.evaluate("JSON.parse(sessionStorage.getItem('sp-seen')||'[]')")
    check(len(seen)==1 and seen[0] in gp.url,'크게 보기가 본 사진을 적어 둠(sp-seen)')
    gp.get_by_role('link',name='닫기').click(); gp.wait_for_url('**/album*'); gp.wait_for_timeout(800)
    n1=gp.locator('.sp-a__new:not(.sp-a__new--event)').count()
    print('after close', n1, gp.url)
    gp.reload(); n2=gp.locator('.sp-a__new:not(.sp-a__new--event)').count(); print('after reload', n2)
    check(n1==1,f'닫고 돌아오면 본 사진 배지 빠짐 ({n1}, 새로 고침 {n2})')
    # 사파리처럼 뒤로 가기로 메모리에서 꺼낸 앨범(새로 안 받음) 흉내: 남은 신규 칸을 본 것으로 적고 pageshow만
    li=gp.locator('li:has(.sp-a__new:not(.sp-a__new--event))').first
    lid=li.get_attribute('id').split('-',1)[1]
    gp.evaluate("id=>{sessionStorage.setItem('sp-seen',JSON.stringify([id]));dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))}",lid)
    n3=gp.locator('.sp-a__new:not(.sp-a__new--event)').count()
    lab=gp.locator(f'[id$="{lid}"] .sp-a__card-link').first.get_attribute('aria-label')
    check(n3==0 and not lab.startswith('신규'),f'메모리에서 꺼낸 앨범도 본 사진 배지·읽는 글 신규 빠짐 ({n3}, {lab})')
    b.close()
print('ALL OK')
