# 찍은 날짜 제대로 읽기(87): 사진은 EXIF(JPEG·PNG), 영상은 아이폰 creationdate → mvhd 만든 시각 → 없으면 파일 시각 (mock)
# 준비(없으면 만듦, ffmpeg·sips 필요): EXIF 넣은 JPEG과 그걸 바꾼 PNG, creationdate와 mvhd가 다른 MOV, mvhd만 있는 MP4. 둘 폴더를 인자로 받음
# HEIC은 크로미움이 그림을 못 열어 여기선 못 봄(단위 시험·tests/exif.test.ts와 맥 sips HEIC으로 확인)
import os,sys,json,struct,subprocess,tempfile
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else tempfile.gettempdir()
JPG,PNG,MOV,MP4=(os.path.join(W,n) for n in ('t-exif.jpg','t-exif.png','t-apple.mov','t-mvhd.mp4'))
if not os.path.exists(JPG):
    # u0.jpg 맨 앞에 DateTimeOriginal 2024:05:01 12:34:56 +09:00
    d=b'2024:05:01 12:34:56\0'; o=b'+09:00\0'
    tiff=b'II'+struct.pack('<HI',42,8)+struct.pack('<HHHII',1,0x8769,4,1,26)+struct.pack('<I',0)
    tiff+=struct.pack('<HHHII',2,0x9003,2,20,56)+struct.pack('<HHII',0x9011,2,7,76)+struct.pack('<I',0)+d+o
    app1=b'Exif\0\0'+tiff; src=open(D+'u0.jpg','rb').read()
    open(JPG,'wb').write(src[:2]+b'\xff\xe1'+struct.pack('>H',len(app1)+2)+app1+src[2:])
    subprocess.run(['sips','-s','format','png',JPG,'--out',PNG],check=True,capture_output=True)
if not os.path.exists(MOV):
    subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','testsrc2=size=640x360:rate=30','-f','lavfi','-i','sine=frequency=440','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',
        '-movflags','use_metadata_tags','-metadata','creation_time=2024-06-01T00:00:00Z','-metadata','com.apple.quicktime.creationdate=2024-05-01T12:30:00+09:00',MOV],check=True)
if not os.path.exists(MP4):
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',D+'v.mp4','-c','copy','-metadata','creation_time=2023-02-03T04:05:06Z',MP4],check=True)
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload')
    files=[JPG,PNG,MOV,MP4,D+'v.mp4',D+'u2.jpg']
    pg.set_input_files('#up-files',files); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=120000)
    rows=[]
    pg.on('request',lambda r: rows.append(json.loads(r.post_data)) if r.method=='POST' and r.url.endswith('/api/media') else None)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=120000)
    got=[(r['kind'],r['takenAt'],r['takenAtSource']) for r in rows]
    print(got)
    check(len(got)==6,'6개 모두 올림')
    if len(got)==6:
        check(got[0]==('photo','2024-05-01T03:34:56.000Z','exif'),'JPEG: EXIF 촬영 시각(시간대 +09:00)')
        check(got[1]==('photo','2024-05-01T03:34:56.000Z','exif'),'PNG: eXIf 촬영 시각')
        check(got[2]==('video','2024-05-01T03:30:00.000Z','exif'),'MOV: 아이폰 creationdate가 mvhd보다 먼저')
        check(got[3]==('video','2023-02-03T04:05:06.000Z','exif'),'MP4: mvhd 만든 시각')
        check(got[4][0]=='video' and got[4][2]=='file','시각 없는 영상은 파일 시각')
        check(got[5][0]=='photo' and got[5][2]=='file','EXIF 없는 사진은 파일 시각')
    b.close()
print('FAILS',FAILS)
