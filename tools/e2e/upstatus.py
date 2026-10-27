# 올리기 파일별 상태(83, 대기열 B): 고를 때 뺀 파일은 이름·이유를 빨간 안내(role=alert)에, 올리는 동안 칸에 올리는 중·올림, 실패하면 그 칸에 못 올림 + 빨간 안내, 다시 누르면 이어서 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
def start(b):
    pg=b.new_page(viewport={'width':390,'height':844})
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload')
    return pg
U0={'name':'u0.jpg','mimeType':'image/jpeg','buffer':open(D+'u0.jpg','rb').read()}
ready="!document.querySelector('#up-actions button').disabled"
tags="[...document.querySelectorAll('.sp-p__upcell')].map(c=>c.querySelector('.sp-p__uptag')?.textContent||'')"
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=start(b)
    # 1) 고를 때 뺀 파일: 이름·이유
    pg.set_input_files('#up-files',[U0,{'name':'IMG_0412.HEIC','mimeType':'image/heic','buffer':b'not an image'},{'name':'clip.webm','mimeType':'video/webm','buffer':b'x'*100},{'name':'memo.pdf','mimeType':'application/pdf','buffer':b'%PDF'}])
    pg.wait_for_function(ready,timeout=60000)
    al=pg.locator('#up-alert')
    check(al.get_attribute('role')=='alert' and al.is_visible(),'빨간 안내 칸이 보이고 role=alert')
    check(al.locator('.sp-p__up-alert-head').inner_text()=='3개는 올릴 수 없어서 뺐어요.','머리글 '+al.inner_text().split('\n')[0])
    rows=al.locator('.sp-p__up-alert-item').all_inner_texts()
    check(rows==['IMG_0412.HEIC · 열 수 없는 파일','clip.webm · 지원하지 않는 형식','memo.pdf · 지원하지 않는 형식'],'파일 이름·이유 '+str(rows))
    check(pg.locator('#up-status').inner_text()=='','진행 글 칸은 비어 있음')
    col=pg.evaluate("getComputedStyle(document.getElementById('up-alert')).color")
    check(col in ('rgb(215, 0, 21)','rgb(255, 105, 97)'),'빨간 글 '+col)
    check(pg.locator('.sp-p__upcell').count()==1 and pg.evaluate(tags)==[''],'올리기 전엔 칸 표시 없음')
    # 2) 새로 고르면 안내 비움
    pg.set_input_files('#up-files',[D+'u0.jpg',D+'u0.jpg']); pg.wait_for_function(ready,timeout=60000)
    check(pg.evaluate("document.getElementById('up-alert').textContent")=='' and al.bounding_box()['height']<=1 and pg.locator('.sp-p__upcell').count()==3,'새로 고르면 안내 비움(고른 것은 더해져 3장)')
    # 3) 둘째 장 보기 파일 PUT이 끊기면: 첫 칸 올림·둘째 칸 못 올림·빨간 안내
    seen=[]; pg.expose_function('noteTags',lambda t: seen.append(tuple(t)))
    pg.evaluate("new MutationObserver(()=>noteTags("+tags+")).observe(document.getElementById('up-grid'),{childList:true,subtree:true})")
    puts={'n':0}
    def cut(route):
        if route.request.method=='PUT' and route.request.url.split('?')[0].endswith('/view'):
            puts['n']+=1
            if puts['n']==2: return route.abort()
        route.continue_()
    pg.route('**/api/media/**',cut)
    pg.get_by_role('button',name='보내지 않고 올리기만').click()
    pg.wait_for_function("document.getElementById('up-alert').textContent!==''",timeout=60000)
    check(pg.evaluate(tags)==['올림','못 올림',''],'첫 칸 올림·둘째 칸 못 올림·셋째는 표시 없음 '+str(pg.evaluate(tags)))
    check(('올리는 중','','') in seen and ('올림','올리는 중','') in seen,'올리는 동안 올리는 중 → 올림 '+str(seen[:6]))
    check(al.inner_text()=='인터넷 연결이 끊겼어요. 1장까지 올렸어요. 다시 누르면 나머지를 이어서 올려요.','실패 안내 '+al.inner_text())
    check(pg.locator('#up-status').inner_text()=='' and pg.locator('#up-progress').is_hidden(),'진행 글·막대는 치움')
    lab=pg.locator('.sp-p__upbtn').nth(1).get_attribute('aria-label')
    check(lab=='2번째 사진 대표, 못 올림','버튼 이름에 상태 '+str(lab))
    check(pg.locator('.sp-p__uptag').first.get_attribute('aria-hidden')=='true','표시 글은 화면 읽기에서 숨김(이름에 있음)')
    check(pg.evaluate("document.activeElement.textContent")=='보내지 않고 올리기만','실패하면 누른 버튼으로 포커스')
    pg.set_viewport_size({'width':320,'height':700})
    # '올리는 중'(가장 긴 글)도 붙여 보고, 칸 안에서 잘리지 않는지(넘치면 띄어쓰기에서 줄바꿈)
    r=pg.evaluate("(()=>{const li=document.querySelector('.sp-p__upcell');const t=document.createElement('span');t.className='sp-p__uptag';t.textContent='올리는 중';li.appendChild(t);const out=[...document.querySelectorAll('.sp-p__uptag')].map(x=>{const a=x.getBoundingClientRect(),c=x.parentElement.getBoundingClientRect();return [x.textContent,x.scrollWidth<=x.clientWidth&&a.right<=c.right+0.5]});t.remove();return out})()")
    check(all(ok for _,ok in r),'320px에서도 표시가 잘리지 않음 '+str(r))
    pg.set_viewport_size({'width':390,'height':844})
    # 4) 다시 누르면 남은 것만 이어서 → 앨범
    pg.unroute('**/api/media/**')
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=60000)
    check(True,'다시 누르면 이어서 올리고 앨범으로')
    pg.close()
    # 5) 그룹을 안 고르면 빨간 안내
    pg=start(b)
    pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function(ready,timeout=60000)
    for c in pg.locator('input[name=group]').all(): c.uncheck()
    pg.get_by_role('button',name='보내지 않고 올리기만').click()
    check(pg.locator('#up-alert').inner_text()=='보여줄 그룹을 하나 이상 골라 주세요.','그룹 안 고르면 빨간 안내')
    pg.locator('input[name=group]').first.check()
    check(pg.evaluate("document.getElementById('up-alert').textContent")=='','그룹을 고르면 그 안내는 지움')
    # 7) 못 여는 파일이 많으면 목록은 10줄까지(9개 + 외 N개)
    pg.set_input_files('#up-files',[{'name':f'bad{i}.heic','mimeType':'image/heic','buffer':b'x'} for i in range(12)]); pg.wait_for_function("document.getElementById('up-alert').textContent!==''",timeout=60000)
    rows=pg.locator('.sp-p__up-alert-item').all_inner_texts()
    check(len(rows)==10 and rows[-1]=='외 3개' and pg.locator('.sp-p__up-alert-head').inner_text()=='12개는 올릴 수 없어서 뺐어요.','목록 10줄까지 '+str(rows[-2:]))
    # 8) 저장 용량이 다 차면(507) 남은 칸 모두 못 올림, 다시 누르면 못 올림 표시를 지우고 이어서
    pg.set_input_files('#up-files',[D+'u0.jpg',D+'u0.jpg']); pg.wait_for_function(ready,timeout=60000)
    n={'v':0}
    def full(route):
        if route.request.method=='PUT' and route.request.url.split('?')[0].endswith('/view'):
            n['v']+=1
            if n['v']==2: return route.fulfill(status=507,body='{}')
        route.continue_()
    pg.route('**/api/media/**',full)
    pg.get_by_role('button',name='보내지 않고 올리기만').click()
    pg.wait_for_function("document.getElementById('up-alert').textContent!==''",timeout=60000)
    check(pg.evaluate(tags)==['올림','못 올림','못 올림'],'5GB 차면 남은 칸 모두 못 올림 '+str(pg.evaluate(tags)))
    check(pg.locator('#up-alert').inner_text().startswith('저장 용량 5GB가 다 찼어요. 1장까지'),'5GB 안내 '+pg.locator('#up-alert').inner_text())
    check('0장' not in pg.locator('#up-alert').inner_text(),'0장 문구 없음')
    seen2=[]; pg.expose_function('noteTags2',lambda t: seen2.append(tuple(t)))
    pg.evaluate("new MutationObserver(()=>noteTags2("+tags+")).observe(document.getElementById('up-grid'),{childList:true,subtree:true})")
    pg.unroute('**/api/media/**')
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=60000)
    check(seen2 and seen2[0]==('올림','올리는 중','') ,'다시 누르면 못 올림을 지우고 이어서 '+str(seen2[:2]))
    pg.close()
    # 6) 200장 넘게 고르면 넘은 것도 안내
    pg=start(b)
    # 못 여는 파일 10개 + 사진 201장: 앞 200개(못 여는 10 + 사진 190)만, 뒤 11개는 200장 넘음. 200장 줄이 맨 앞이라 '외 N개'가 파일 수와 맞음
    pg.set_input_files('#up-files',[{'name':f'bad{i}.heic','mimeType':'image/heic','buffer':b'x'} for i in range(10)]+[U0]*201); pg.wait_for_function(ready,timeout=180000)
    rows=pg.locator('.sp-p__up-alert-item').all_inner_texts()
    check(pg.locator('.sp-p__upcell').count()==190 and rows[0]=='뒤의 11개 · 한 묶음에 200장까지' and len(rows)==10 and rows[-1]=='외 2개' and pg.locator('.sp-p__up-alert-head').inner_text()=='21개는 올릴 수 없어서 뺐어요.','200장 넘음 안내·목록 자르기 '+str([rows[0],rows[-1]]))
    pg.close()
    b.close()
print('FAILS',FAILS)
