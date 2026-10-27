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
    pg.screenshot(path=D+'upstatus-fail.png')
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
    pg.close()
    # 6) 200장 넘게 고르면 넘은 것도 안내
    pg=start(b)
    pg.set_input_files('#up-files',[D+'u0.jpg']*201); pg.wait_for_function(ready,timeout=180000)
    rows=pg.locator('.sp-p__up-alert-item').all_inner_texts()
    check(pg.locator('.sp-p__upcell').count()==200 and rows==['200장 넘게 고른 1개 · 한 번에 200장까지'] and pg.locator('.sp-p__up-alert-head').inner_text()=='1개는 올릴 수 없어서 뺐어요.','200장 넘음 안내 '+str(rows))
    pg.close()
    b.close()
print('FAILS',FAILS)
