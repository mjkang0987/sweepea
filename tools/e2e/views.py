# 보신 기록(95, mock): 가족이 본 사진을 엄빠 크게 보기에 "외할아버지가 봤어요"로(이름만, 횟수 없음)
# 가족 크게 보기 열면 남음 · 넘겨 보기 가운데 1.5초 머물면 남음 · 엄빠가 본 건 안 셈 · 승인 대기는 안 남음 · 입장 화면 안내 한 줄
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def seen(pg,vid):
    pg.goto(B+'/view/'+vid); s=pg.locator('.sp-v__seen')
    return s.inner_text().strip() if s.count() else ''
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg',D+'u1.jpg',D+'u2.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    ids=pg.eval_on_selector_all('.sp-p__cell-link',"a=>a.map(x=>x.href.split('/view/')[1].split('?')[0])")
    check(len(ids)==3,'사진 3장')
    check(seen(pg,ids[0])=='','아무도 안 봤으면 줄 없음(엄빠가 연 건 안 셈)')
    # 가족 들이기: 외할아버지(승인), 큰이모(승인 대기)
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    def enter(name):
        gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
        gp.fill('#who-name',name); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
        return gp
    gp=b.new_context(viewport={'width':390,'height':844}).new_page(); gp.goto(B+'/i/'+code)
    check(gp.get_by_text('엄마아빠에게 누가 봤는지 보여요').is_visible(),'입장 화면에 안내 한 줄')
    gp.close()
    gp=enter('외할아버지'); ap=enter('큰이모')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할아버지').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    # 승인 대기 큰이모가 열어도 안 남음
    ap.goto(B+'/album/'+ids[0])
    # 외할아버지: 크게 보기 열기 → 남음
    gp.goto(B+'/album/'+ids[0])
    check(seen(pg,ids[0])=='외할아버지가 봤어요','크게 보기 열면 "외할아버지가 봤어요"(승인 대기는 빠짐)')
    gp.goto(B+'/album/'+ids[0]); check(seen(pg,ids[0])=='외할아버지가 봤어요','여러 번 봐도 이름 한 번, 횟수 없음')
    # 크게 보기에서 옆으로 넘기면(페이지를 받아 옴) 그 사진도
    gp.get_by_role('link',name='다음 사진').click(); gp.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='2 / 3'"); gp.wait_for_timeout(300)
    check(seen(pg,ids[1])=='','크게 보기에서 휙 넘긴 사진은 바로 안 남음')
    gp.wait_for_timeout(1700)
    check(seen(pg,ids[1])=='외할아버지가 봤어요','크게 보기에서 넘긴 사진은 1.5초 머물면 남음')
    # 넘겨 보기: 세 번째 사진을 가운데로 → 1.5초 안엔 안 남고 지나면 남음
    gp.goto(B+'/album'); gp.wait_for_timeout(300)
    gp.locator('#p-'+ids[2]).scroll_into_view_if_needed(); gp.evaluate("id=>document.getElementById('p-'+id).scrollIntoView({inline:'center',behavior:'instant'})",ids[2])
    gp.wait_for_timeout(600); check(seen(pg,ids[2])=='','넘겨 보기: 잠깐 지나간 사진은 안 남음')
    gp.wait_for_timeout(1500); check(seen(pg,ids[2])=='외할아버지가 봤어요','넘겨 보기: 가운데 1.5초 머물면 남음')
    # 받침 있는 이름 + 조사
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 큰이모').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    ap.goto(B+'/album/'+ids[1])
    check(seen(pg,ids[1])=='외할아버지·큰이모가 봤어요','두 사람은 · 로 잇고 처음 본 순')
    pg.screenshot(path=D+'../shots/views-parent.png') if os.path.isdir(D+'../shots') else None
    # 넘기면(엄빠 크게 보기 스와이프) 그 사진의 줄로 바뀜
    pg.goto(B+'/view/'+ids[0]); pg.get_by_role('link',name='다음 사진').click(); pg.wait_for_function("document.querySelector('.sp-v__pos').textContent.trim()=='2 / 3'")
    pg.wait_for_function("document.querySelector('.sp-v__seen')?.textContent.includes('큰이모')")
    check(True,'엄빠 크게 보기 넘기면 그 사진의 본 사람으로 바뀜')
    # API: 잘못된 요청 거절, 출입증 없으면 401
    r=gp.request.post(B+'/api/views',data={'ids':['x']}); check(r.status==400,'잘못된 id 400')
    r=gp.request.post(B+'/api/views',data={'ids':[ids[0]]*51}); check(r.status==400,'51장 400')
    r=b.new_context().request.post(B+'/api/views',data={'ids':[ids[0]]}); check(r.status==401,'출입증 없으면 401')
    b.close()
print('FAILS',fails) if fails else print('ALL OK')
