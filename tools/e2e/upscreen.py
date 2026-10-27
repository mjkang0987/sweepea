# 부모 올리기 화면 (실제 JPEG, EXIF 날짜)
import io
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
files=[]
for i,(w,h,c,date) in enumerate([(3024,4032,(240,180,120),'2026:10:21 15:30:00'),(4032,3024,(120,200,160),'2026:09:03 09:10:00'),(2000,2000,(160,160,230),None)]):
    im=Image.new('RGB',(w,h),c); ImageDraw.Draw(im).ellipse((w*.3,h*.3,w*.7,h*.7),fill=(255,255,255))
    ex=im.getexif()
    if date: ex.get_ifd(0x8769)[0x9003]=date
    p=D+f'u{i}.jpg'; im.save(p,'JPEG',quality=90,exif=ex); files.append(p)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); c.grant_permissions(['clipboard-read','clipboard-write']); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.get_by_role('link',name='사진 추가하기').click(); pg.wait_for_url('**/upload')
    check(pg.get_by_role('button',name='올리고 카톡으로 보내기').is_disabled(),'고르기 전엔 올리기 버튼 꺼짐')
    check(not pg.locator('#up-done').is_visible(),'끝 카드는 처음엔 숨김')
    pg.set_input_files('#up-files',files); pg.wait_for_function("document.getElementById('up-title').textContent.includes('3장')",timeout=30000)
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    size=pg.locator('#up-size').text_content(); check('MB' in size,'줄인 크기 표시: '+size)
    pg.get_by_role('button',name='2번째 사진 대표').click()
    check(pg.get_by_role('button',name='2번째 사진 대표').get_attribute('aria-pressed')=='true','대표 사진 바꾸기')
    check(pg.evaluate("document.activeElement.getAttribute('aria-label')")=='2번째 사진 대표','대표 고른 뒤에도 초점 유지')
    pg.screenshot(path=D+'up-1.png')
    pg.get_by_role('button',name='올리고 카톡으로 보내기').click()
    pg.wait_for_selector('#up-done:not([hidden])',timeout=60000)
    check(not pg.locator('#up-form').is_visible(),'다 올리면 고르기 화면은 숨김')
    link=pg.locator('#up-link').input_value(); check('/i/' in link,'다 올리고 공유 주소: '+link); pg.screenshot(path=D+'up-2.png')
    pg.get_by_role('link',name='앨범으로').click(); pg.wait_for_url('**/home')
    check(pg.locator('.sp-p__cell').count()==3,'부모 앨범에 3장')
    pg.wait_for_function("[...document.querySelectorAll('.sp-p__cell-img')].every(i=>i.complete && i.naturalWidth>0)",timeout=15000)
    check(True,'부모 앨범 썸네일이 실제로 보임')
    check('2026년 10월' in pg.content() and '2026년 9월' in pg.content(),'EXIF 찍은 날로 월 묶음')
    pg.screenshot(path=D+'up-3.png')
    b.close()
from PIL import Image as I
ims=[I.open(D+f'up-{n}.png') for n in (1,2,3)]
o=I.new('RGB',(sum(i.width for i in ims)+20,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(D+'up-all.png'); print('ALL OK')
