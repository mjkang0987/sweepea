# 사진 해상도·정보(142): 위치가 든 4032×3024 사진을 올리면 서버 파일은 해상도 그대로, 찍은 날·기종은 남고 위치(GPS)는 없다
import io, layerfix, os, random, tempfile
from PIL import Image
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
W=tempfile.mkdtemp(); f=os.path.join(W,'IMG_0001.jpg')
random.seed(1); im=Image.effect_noise((4032,3024),40).convert('RGB')  # 무늬가 있어야 용량이 실제처럼
ex=im.getexif(); ex[0x010f]='Apple'; ex[0x0110]='iPhone 15 Pro Max'
sub=ex.get_ifd(0x8769); sub[0x9003]='2025:05:05 10:20:30'; sub[0x9011]='+09:00'
gps=ex.get_ifd(0x8825); gps[1]='N'; gps[2]=(37.0,33.0,59.4); gps[3]='E'; gps[4]=(126.0,58.0,40.8)
im.save(f,'JPEG',quality=95,exif=ex)
check(0x8825 in Image.open(f).getexif(),'올릴 사진에 위치가 들어 있음(검사 준비)')
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[f]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=120000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=120000)
    mid=pg.locator('.sp-p__cell').first.get_attribute('id')[2:]
    pg.goto(B+'/view/'+mid); src=pg.locator('.sp-v__media').first.get_attribute('src')
    data=pg.context.request.get(B+src).body(); got=Image.open(io.BytesIO(data)); gx=got.getexif()
    print('  저장된 파일',got.size,len(data)//1024,'KB')
    check(got.size==(4032,3024),'해상도 그대로(4032×3024)')
    check(gx.get_ifd(0x8769).get(0x9003)=='2025:05:05 10:20:30' and gx.get_ifd(0x8769).get(0x9011)=='+09:00','찍은 날·시간대 그대로')
    check(gx.get(0x010f)=='Apple' and gx.get(0x0110)=='iPhone 15 Pro Max','기종 그대로')
    check(0x8825 not in gx and not gx.get_ifd(0x8825),'위치(GPS) 없음')
    b.close()
print('FAILS',FAILS)
