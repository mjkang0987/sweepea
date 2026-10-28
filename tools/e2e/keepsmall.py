# 이미 작은 사진은 다시 저장하지 않기(97): 작은 JPEG는 정보(EXIF·GPS)만 뺀 원본이 다시 저장한 것보다 작거나 같으면 그대로,
# 아니면·회전 정보가 있으면·큰 사진은 다시 저장. 어떤 경우에도 올라간 보기용에 위치·기기 정보가 없다 (mock, 인자 webkit이면 사파리 엔진)
import io,os,sys,tempfile,base64
from PIL import Image
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
T=tempfile.mkdtemp()
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def make(name,size,q,orient=1,gps=True):
    im=Image.new('RGB',size)
    px=im.load()
    for x in range(0,size[0],4):
        for y in range(0,size[1],4): px[x,y]=((x*7)%256,(y*5)%256,((x+y)*3)%256)
    ex=Image.Exif()
    if orient!=1: ex[0x0112]=orient
    ex[0x010f]='Apple'
    if gps: ex[0x8825]={1:'N',2:(37.0,33.0,12.0),3:'E',4:(126.0,58.0,40.0)}
    p=f'{T}/{name}.jpg'; im.save(p,'JPEG',quality=q,exif=ex); return p
kakao=make('kakao',(1280,960),55)          # 낮은 화질 작은 사진 → 그대로(정보만 뺌)
fine=make('fine',(1600,1200),100)           # 화질 100 작은 사진 → 다시 저장한 쪽이 작음
big=make('big',(3000,2000),80)              # 큰 사진 → 다시 저장(긴 변 2048)
rot=make('rot',(1200,900),55,orient=6)      # 회전 정보 → 다시 저장
files=[kakao,fine,big,rot]
with sync_playwright() as p:
    br=(p.webkit if 'webkit' in sys.argv else p.chromium).launch(); pg=br.new_page(viewport={'width':390,'height':844})
    # 브라우저가 보낸 Blob 본문은 요청 기록에 안 남아서 fetch를 감싸 받아 둔다
    pg.add_init_script("""window.__views=[];const f=window.fetch;window.fetch=async(u,o)=>{
      if(o&&o.method==='PUT'&&String(u).endsWith('/view')&&o.body instanceof Blob){const b=new Uint8Array(await o.body.arrayBuffer());let s='';for(const c of b)s+=String.fromCharCode(c);window.__keep(btoa(s));}
      return f(u,o)}""")
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',files)
    pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    got=[]
    pg.expose_function('__keep',lambda b:got.append(base64.b64decode(b)))
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    check(len(got)==4,f'보기용 4장 올라감 ({len(got)})')
    raw={n:open(f,'rb').read() for n,f in zip(['kakao','fine','big','rot'],files)}
    # 사파리는 다시 저장할 때 자기 EXIF(해상도 정도)를 붙이므로 '위치·제조사가 없음'으로 본다
    for b in got:
        ex=Image.open(io.BytesIO(b)).getexif()
        check(0x8825 not in ex and 0x010f not in ex and b'Apple' not in b,f'보기용({len(b)}바이트)에 위치·기기 정보 없음')
    ims=[Image.open(io.BytesIO(b)) for b in got]
    sizes=sorted(im.size for im in ims)
    check((2048,1365) in sizes,f'큰 사진은 긴 변 2048로 줄임 {sizes}')
    check((900,1200) in sizes,'회전 정보 사진은 돌려서 다시 저장(900×1200)')
    # 카톡 사진: 그림 데이터가 원본과 바이트 그대로(정보만 빠짐)
    sos=raw['kakao'].index(b'\xff\xda')
    check(any(b.endswith(raw['kakao'][sos:]) and len(b)<len(raw['kakao']) for b in got),'낮은 화질 작은 사진은 원본 그림 그대로(정보만 뺌, 더 작아짐)')
    check(not any(raw['fine'][raw['fine'].index(b'\xff\xda'):] in b for b in got),'화질 100 작은 사진은 다시 저장한 쪽(더 작음)')
    check(all(len(b)<=len(raw['fine']) for b in got),'어떤 보기용도 원본보다 크지 않음')
    # 앨범에서 그대로 올린 사진이 열리는지
    pg.goto(B+'/home'); pg.wait_for_timeout(800)
    ok=pg.evaluate("Promise.all([...document.querySelectorAll('img')].filter(i=>i.src.includes('/m/')).map(i=>i.decode().then(()=>i.naturalWidth>0,()=>false)))")
    check(len(ok)>=4 and all(ok),f'홈에서 사진 모두 열림 {ok}')
    br.close()
print('FAILS',fails)
