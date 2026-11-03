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
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.get_by_role('link',name='사진 추가').click(); pg.wait_for_url('**/upload')
    check(pg.get_by_role('button',name='올리고 카톡으로 보내기').is_disabled(),'고르기 전엔 올리기 버튼 꺼짐')
    check(not pg.locator('#up-done').is_visible(),'끝 카드는 처음엔 숨김')
    # 141: 올리기 기준은 접힌 details, 누르면 사진·영상 기준이 보임
    rules=pg.locator('#up-rules'); check(not rules.locator('.sp-p__up-rules-list').is_visible(),'올리기 기준은 처음엔 접힘')
    pg.get_by_text('올리기 기준 자세히').click(); rt=rules.inner_text()
    check(rules.locator('.sp-p__up-rules-list').is_visible() and all(k in rt for k in ['4032','위치','2GB','3분','200개','5GB']),'올리기 기준 펼침: 사진 4032·위치만 지움·영상 2GB·3분·200개·5GB')
    pg.set_input_files('#up-files',files); pg.wait_for_function("document.getElementById('up-title').textContent.includes('3장')",timeout=30000)
    # 161: 보내기는 고르자마자 켜지고, 칸은 준비(줄이기)가 끝난 것부터 채워진다. 크기 줄은 없앰
    check(not pg.locator('#up-actions button').first.is_disabled(),'고르자마자 보내기 켜짐')
    pg.wait_for_function("!document.querySelector('.sp-p__upcell--wait')",timeout=30000)
    check(pg.locator('#up-size').count()==0,'크기 줄 없음')
    # 카톡 대표 사진 고르기는 뺐다(112): 칸 이름은 'N번째 사진', 칸 위 버튼은 빼기 ✕뿐
    check(pg.locator('.sp-p__upgrid button').count()==3 and pg.locator('.sp-p__upgrid button.sp-p__upx').count()==3 and pg.get_by_role('img',name='2번째 사진').count()==1 and pg.get_by_role('button',name='2번째 사진 빼기').count()==1,'칸은 그림 + 빼기 ✕(대표 고르기 없음)')
    # 아이·보여줄 그룹은 아래 막대 안
    check(pg.locator('#up-actions').get_by_role('group',name='보여줄 그룹').count()==1 and pg.locator('#up-actions input[name=group]').count()>=1,'보여줄 그룹은 아래 막대 안')
    check(pg.locator('#up-cover-hint').count()==0,'대표 사진 안내 없음')
    pg.screenshot(path=D+'up-1.png')
    pg.get_by_role('button',name='올리고 카톡으로 보내기').click()
    pg.wait_for_selector('#up-done:not([hidden])',timeout=60000)
    check(not pg.locator('#up-form').is_visible(),'다 올리면 고르기 화면은 숨김')
    link=pg.locator('#up-link').input_value(); check('/i/' in link,'다 올리고 공유 주소: '+link); pg.screenshot(path=D+'up-2.png')
    pg.get_by_role('link',name='앨범으로').click(); pg.wait_for_url('**/home')
    check(pg.locator('.sp-p__cell').count()==3,'부모 앨범에 3장')
    pg.wait_for_function("[...document.querySelectorAll('.sp-p__cell-img')].every(i=>i.complete && i.naturalWidth>0)",timeout=15000)
    check(True,'부모 앨범 썸네일이 실제로 보임')
    # 117b(2026-11-01)부터 달 제목 대신 그 달 첫 칸에 표식(#m-YYYY-MM)
    check(pg.locator('.sp-p__anchor[id$="-10"]').count()==1 and pg.locator('.sp-p__anchor[id$="-09"]').count()==1,'EXIF 찍은 날로 달 나눔(10월·9월 첫 칸 표식)')
    pg.screenshot(path=D+'up-3.png')
    b.close()
from PIL import Image as I
ims=[I.open(D+f'up-{n}.png') for n in (1,2,3)]
o=I.new('RGB',(sum(i.width for i in ims)+20,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(D+'up-all.png'); print('ALL OK')
