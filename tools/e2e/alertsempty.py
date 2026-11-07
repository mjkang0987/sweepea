# 184 알림 빈 글: 사진이 없으면 '사진을 올리고 카톡으로 보내 보세요', 올린 뒤엔 '가족이 … 남기면 여기에 모여요' (mock, 인자: 스크린샷 폴더)
import sys
from PIL import Image
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
f=W+'/ae.jpg'; Image.new('RGB',(800,600),(120,200,160)).save(f,'JPEG')
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_page(viewport={'width':390,'height':844})
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-10-01'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/reactions'); n=pg.locator('.sp-p__note').inner_text()
    check('사진을 올리고 카톡으로 보내 보세요' in n,f'사진 없을 때: {n}')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[f]); pg.wait_for_function("!document.querySelector('.sp-p__upcell--wait')",timeout=30000)
    pg.get_by_role('button',name='올리고 카톡으로 보내기').click(); pg.wait_for_selector('#up-done:not([hidden])',timeout=60000)
    pg.goto(B+'/reactions'); n=pg.locator('.sp-p__note').inner_text()
    check('남기면 여기에 모여요' in n and '올리고' not in n,f'올린 뒤: {n}')
    pg.wait_for_timeout(600); pg.screenshot(path=W+'/ae-after.png')
    br.close()
print('FAILS',fails)
