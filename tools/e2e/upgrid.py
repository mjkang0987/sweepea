# 올리기 고른 사진 칸 간격(사용자 2026-10-27 "좌우 상하 달라"): 좌우·상하 모두 4px, 칸은 정사각형. 폰(4칸)·PC(6칸) (mock)
import os
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h,cols in [(390,844,4),(1280,900,6)]:
        pg=b.new_page(viewport={'width':w,'height':h})
        pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
        pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
        pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
        pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']*(cols+1)); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
        r=pg.evaluate("""(cols)=>{const c=[...document.querySelectorAll('.sp-p__upcell')].map(e=>e.getBoundingClientRect());
          return {w:c[0].width,h:c[0].height,col:c[1].left-c[0].right,row:c[cols].top-c[0].bottom}}""",cols)
        check(abs(r['col']-4)<0.5 and abs(r['row']-4)<0.5,'%d칸: 좌우 %.1f·상하 %.1f px'%(cols,r['col'],r['row']))
        check(abs(r['w']-r['h'])<0.5,'%d칸: 칸은 정사각형 (%.1fx%.1f)'%(cols,r['w'],r['h']))
        pg.close()
    b.close()
print('FAILS',FAILS)
