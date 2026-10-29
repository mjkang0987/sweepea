# 사진 한 장 저장(사용자 2026-10-29 "사진 저장 누르니까 다운로드로 가는데, 앨범으로 가는 게 맞는데"):
# 아이폰(터치)은 공유 창(navigator.share, '이미지 저장' → 사진 앱)으로, 안드로이드·PC는 내려받기. 공유를 그만두면 아무 일 없음 (mock, 인자: 폴더 엔진)
import os,sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else '/tmp'
eng=sys.argv[2] if len(sys.argv)>2 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
STUB="""window.__shared=null;navigator.canShare=()=>true;navigator.share=async(d)=>{window.__shared=d.files.map(f=>[f.name,f.type,f.size]);if(window.__abort)throw new DOMException('x','AbortError');if(window.__block)throw new DOMException('x','NotAllowedError')};"""
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    phone=br.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=eng=='chromium')
    phone.add_init_script(STUB)
    pg=phone.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg'])
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.goto(B+'/home'); pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    check(pg.evaluate("matchMedia('(pointer: coarse)').matches"),'휴대폰 흉내(터치)')
    pg.get_by_role('link',name='저장').first.tap() if eng=='chromium' else pg.get_by_role('link',name='저장').first.click()
    pg.wait_for_function("window.__shared",timeout=10000)
    sh=pg.evaluate("window.__shared")
    check(sh and sh[0][1].startswith('image/') and sh[0][2]>1000,f'휴대폰: 공유 창으로 사진 파일 {sh}')
    check('/view/' in pg.url,'공유 뒤에도 같은 화면(다운로드로 안 넘어감)')
    # 그만두기: 아무 일 없음(내려받기로 안 넘어감)
    pg.evaluate("window.__abort=1;window.__shared=null")
    dl=[]; pg.on('download',lambda d: dl.append(d))
    pg.get_by_role('link',name='저장').first.click(); pg.wait_for_timeout(1500)
    check(pg.evaluate("window.__shared") is not None and not dl,'공유 창에서 그만두면 내려받기 없음')
    # 휴대폰이 공유 창을 막으면(누른 뒤 늦음): 내려받기로 넘기지 않고 '한 번 더 눌러 주세요'(실기기 "다운로드로 들어가는디")
    pg.evaluate("window.__abort=0;window.__block=1")
    pg.get_by_role('link',name='저장').first.click(); pg.wait_for_timeout(800)
    check(not dl and '한 번 더 눌러 주세요' in pg.locator('.sp-toast').last.inner_text(),'공유 창이 막히면 내려받기 대신 다시 누르기 안내')
    # 안드로이드: 공유 창엔 갤러리 저장이 없어 내려받기(갤러리 'Download'에 보임, 사용자 "안드로이드는 공유하기 뜨는데")
    if eng=='chromium':
        an=br.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,accept_downloads=True,user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36')
        an.add_cookies(phone.cookies()); an.add_init_script(STUB); a=an.new_page(); a.goto(pg.url)
        with a.expect_download(timeout=10000) as d2:
            a.get_by_role('link',name='저장').first.tap()
        check(a.evaluate("window.__shared") is None and d2.value.suggested_filename.endswith('.jpg'),'안드로이드: 공유 창 대신 내려받기')
        check("'Download' 앨범" in a.locator('.sp-toast').last.inner_text(),'안드로이드: 갤러리 Download 앨범 안내')
        an.close()
    # PC: 내려받기 그대로
    cookies=phone.cookies(); pc=br.new_context(viewport={'width':1280,'height':900},accept_downloads=True); pc.add_cookies(cookies); pc.add_init_script(STUB)
    q=pc.new_page(); q.goto(pg.url)
    with q.expect_download(timeout=10000) as d:
        q.get_by_role('link',name='저장').first.click()
    check(d.value.suggested_filename.endswith(('.jpg','.jpeg','.webp')) and q.evaluate("window.__shared") is None,f'PC: 그대로 내려받기 ({d.value.suggested_filename})')
    br.close()
print('FAILS',fails)
