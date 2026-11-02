# 영상 찍은 장소 지우기(138): 위치(©xyz·loci·mdta location)가 든 영상을 올리면 서버에 저장된 파일에 위치가 없다
import layerfix, os, subprocess, tempfile
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
W=tempfile.mkdtemp(); a=os.path.join(W,'a.mov'); f=os.path.join(W,'loc.mov')
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','testsrc=size=640x360:rate=30:duration=2','-f','lavfi','-i','sine=duration=2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest','-metadata','location=+37.5665+126.9780/',a],check=True)
subprocess.run(['ffmpeg','-loglevel','error','-y','-i',a,'-c','copy','-movflags','use_metadata_tags','-metadata','com.apple.quicktime.location.ISO6709=+37.5665+126.9780+050.000/',f],check=True)
check(b'37.5665' in open(f,'rb').read(),'올릴 영상에 위치가 들어 있음(검사 준비)')
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_context(viewport={'width':390,'height':844}).new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[f]); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=120000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=120000)
    vid=pg.locator('.sp-p__cell').first.get_attribute('id')[2:]
    pg.goto(B+'/view/'+vid); src=pg.locator('video').first.get_attribute('src')
    data=pg.context.request.get(B+src).body()
    check(len(data)>1000 and b'37.5665' not in data and b'loci' not in data and b'quicktime.location' not in data,f'서버에 저장된 영상에 위치 없음({len(data)}바이트)')
    out=os.path.join(W,'got.mov'); open(out,'wb').write(data)
    r=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name','-of','csv=p=0',out],capture_output=True,text=True)
    check('h264' in r.stdout,'저장된 영상은 그대로 재생 가능(트랙 '+r.stdout.strip().replace(chr(10),',')+')')
    b.close()
print('FAILS',FAILS)
