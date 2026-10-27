# 엄빠 앨범 엇갈린 배열: 세로 간격 = 가로 간격(4px)인지 2열·4열에서 잼
import layerfix,sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'; S=D+'../shots/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
M="""()=>{const cs=[...document.querySelectorAll('.sp-p__cell')].map(e=>e.getBoundingClientRect());
 const v=[],h=[];for(const a of cs)for(const b of cs){if(a===b)continue;
  if(Math.abs(a.left-b.left)<1&&b.top>a.bottom-1){const g=b.top-a.bottom;if(g<20)v.push(+g.toFixed(2))}
  if(Math.abs(a.top-b.top)<200&&b.left>a.right-1&&b.left-a.right<20)h.push(+(b.left-a.right).toFixed(2))}
 return {v:[...new Set(v)].sort(),h:[...new Set(h)].sort()}}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+f for f in ['u0.jpg','u1.jpg','u2.jpg','tall.jpg','u0.jpg','tall.jpg','u1.jpg','u2.jpg']]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=90000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=90000)
    for w in (390,375,430,1280):
        pg.set_viewport_size({'width':w,'height':900}); pg.goto(B+'/home'); r=pg.evaluate(M)
        print(w,r)
        check(all(abs(x-4)<=0.05 for x in r['v']) and all(abs(x-4)<=0.05 for x in r['h']),f'{w}px 세로·가로 간격 4px {r}')
    pg.set_viewport_size({'width':390,'height':844}); pg.goto(B+'/home'); pg.screenshot(path=S+'gaps.png')
print('FAILS',fails)
