# 162: 영상이 처음 열 때만 안 열리면(아이폰 사례) 저절로 한 번 더 해서 올라감, 두 번 다 안 되면 안내 (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
# 처음 N번 영상 src를 넣으면 error를 낸다(브라우저가 영상을 못 연 것처럼)
FAIL_FIRST="""(()=>{let n=%d;const d=Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype,'src');Object.defineProperty(HTMLMediaElement.prototype,'src',{configurable:true,get(){return d.get.call(this)},set(v){if(v&&n>0){n--;d.set.call(this,'blob:bad');return}d.set.call(this,v)}})})()"""
def run(b,fails):
    pg=b.new_page(viewport={'width':390,'height':844}); pg.add_init_script(FAIL_FIRST%fails)
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'v.mp4'])
    pg.wait_for_function("!document.querySelector('.sp-p__upcell--wait')",timeout=90000)
    return pg
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=run(b,1)
    check(pg.locator('.sp-p__upcell').count()==1 and pg.evaluate("document.getElementById('up-alert').textContent")=='','처음만 안 열리면 저절로 다시 해서 칸이 채워짐(안내 없음)')
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=60000)
    check(pg.locator('.sp-p__cell').count()==1,'올라감')
    pg.close()
    pg=run(b,2)
    check(pg.locator('.sp-p__upcell').count()==0 and 'v.mp4 · 열 수 없는 파일' in pg.locator('#up-alert').inner_text(),'두 번 다 안 되면 안내 '+pg.locator('#up-alert').inner_text())
    b.close()
print('FAILS',FAILS)
