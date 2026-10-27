# 영상 폰에서 줄이기(80): 큰 영상은 1080p로 줄여 한 번에 올리고(진행률 %·진행 막대·화면 켜 두기 안내·원본 안내), 작은 영상과 줄이기를 못 하는 브라우저는 원본 그대로 (mock)
# 준비(없으면 만듦, ffmpeg 필요): 아이폰처럼 H.264+AAC·세로 회전 정보가 있는 2560x1440 20Mbps 6초 영상, 재생되는 130MB 영상(bigvideo.py와 같은 방법). 둘 폴더를 인자로 받음
import os,sys,struct,json,subprocess,tempfile
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
W=sys.argv[1] if len(sys.argv)>1 else tempfile.gettempdir()
BIG=os.path.join(W,'big.mp4'); QHD=os.path.join(W,'qhd-rot.mp4')
if not os.path.exists(BIG):
    with open(BIG,'wb') as f:
        f.write(open(D+'v.mp4','rb').read()); pad=130*1024*1024; f.write(struct.pack('>I',pad+8)+b'free'); f.write(b'\0'*pad)
if not os.path.exists(QHD):
    raw=os.path.join(W,'qhd.mp4')
    subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','testsrc2=size=2560x1440:rate=30','-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','6','-c:v','libx264','-b:v','20M','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',raw],check=True)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-display_rotation','90','-i',raw,'-c','copy',QHD],check=True)
def probe(path):
    out=json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height:stream_side_data=rotation','-of','json',path],capture_output=True,text=True).stdout)
    return out['streams']
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
WRAP="const g=window.fetch;window.fetch=(u,o)=>{if(o&&o.method==='PUT'&&String(u).includes('/api/media/'))notePut([String(u).split('?')[0].split('/').pop(),o.body?.size??0]);return g(u,o)}"
def start(b,init=None):
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    if init: pg.add_init_script(init)
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload')
    return c,pg
def pick(pg,files):
    msgs=[]; pg.expose_function('note',lambda t: msgs.append(t))
    pg.evaluate("""new MutationObserver(()=>note(document.getElementById('up-status').textContent+'|'+document.getElementById('up-shrink-hint').hidden+'|'+document.getElementById('up-size').textContent)).observe(document.getElementById('up-status'),{childList:true,characterData:true,subtree:true})""")
    pg.set_input_files('#up-files',files); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=180000)
    return msgs
def send(pg,timeout=120000):
    """보내지 않고 올리기만 → 보낸 PUT 크기와 만든 사진 행(id·종류·가로세로)"""
    puts=[]; rows=[]
    pg.expose_function('notePut',lambda a: puts.append(a)); pg.evaluate(WRAP)
    def on(r):
        if r.request.method=='POST' and r.url.endswith('/api/media'):
            rows.append(dict(json.loads(r.request.post_data),id=r.json()['id']))
    pg.on('response',on)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=timeout)
    return puts,rows
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1) 큰 세로 영상 + 작은 영상 + 사진: 큰 것은 1080p로 줄여서 한 번에, 작은 영상은 원본 그대로
    c,pg=start(b)
    check('스위피는 원본을 따로 보관하지 않으니' in pg.locator('.sp-p__up-note').inner_text(),'원본·줄임 안내가 보임')
    msgs=pick(pg,[QHD,D+'v.mp4',D+'u0.jpg'])
    pct=[m.split('|')[0] for m in msgs if m.startswith('영상 줄이는 중… 1 / 3 · ')]
    check(any(not t.endswith(' 0%') for t in pct) and all(t.endswith('0%') for t in pct),'영상 줄이는 중… 1 / 3 · N%, 10% 단위로만 읽어 줌 '+str(pct))
    check(len(pct)==len(set(pct)),'같은 글을 거듭 읽어 주지 않음')
    check(len(pct)>0 and all(m.split('|')[1]=='false' and m.split('|')[2]=='줄이는 중' for m in msgs if m.startswith('영상 줄이는 중… 1 / 3 · ')),'줄이는 동안 화면 켜 두기 안내·크기 칸 줄이는 중')
    check(pg.locator('#up-bar').is_hidden(),'다 줄이면 진행 막대 숨김')
    check(pg.locator('#up-shrink-hint').is_hidden() and 'MB' in pg.locator('#up-size').inner_text(),'다 줄이면 안내 숨김·크기 보임 ('+pg.locator('#up-size').inner_text()+')')
    bars=[]; pg.expose_function('noteBar',lambda v: bars.append(v))
    pg.evaluate("new MutationObserver(()=>{const b=document.getElementById('up-bar');noteBar((b.hidden?'h':'v')+b.value)}).observe(document.getElementById('up-bar'),{attributes:true})")
    n0=len(msgs)
    puts,rows=send(pg)
    up=[m.split('|')[0] for m in msgs[n0:] if m.startswith('올리는 중…')]
    check(any(u.endswith('· 100%') for u in up) and any(u.startswith('올리는 중… 3 / 3 · ') for u in up),'올릴 때도 퍼센트(사진 포함, 마지막 100%) '+str(up[:2]+up[-1:]))
    check(any(x.startswith('v') for x in bars) and bars and bars[-1].startswith('h'),'올릴 때 진행 막대 보였다가 끝나면 숨김 '+str(bars[-3:]))
    views=[s for s in puts if s[0]=='view']
    check(not any(s[0]=='multipart' for s in puts),'나눠 올리기 없이 한 번에')
    check(len(views)==3 and any(v[1]==os.path.getsize(D+'v.mp4') for v in views),'작은 영상은 원본 그대로 '+str([v[1] for v in views]))
    qrow=rows[0]
    check(qrow['kind']=='video' and (qrow['width'],qrow['height'])==(1080,1920),'세로 영상은 1080x1920으로 적음 (%sx%s)'%(qrow['width'],qrow['height']))
    check(views[0][1]<os.path.getsize(QHD)*0.6,'큰 영상은 줄인 크기로 (%d → %d)'%(os.path.getsize(QHD),views[0][1]))
    # 줄인 영상을 받아서: H.264 1080x1920(회전 정보로 세로여도 됨), 소리 남음, 크게 보기에서 재생됨
    pg.goto(B+'/view/'+qrow['id']); pg.wait_for_selector('video')
    src=pg.evaluate("(()=>{const v=[...document.querySelectorAll('video')].find(x=>x.currentSrc||x.src);return v?(v.currentSrc||v.src):''})()")
    body=c.request.get(src).body(); out=os.path.join(W,'shrunk.mp4'); open(out,'wb').write(body)
    st=probe(out); vs=[x for x in st if x['codec_type']=='video']; aus=[x for x in st if x['codec_type']=='audio']
    rot=(vs[0].get('side_data_list') or [{}])[0].get('rotation',0) if vs else None
    dims=(vs[0]['width'],vs[0]['height']) if vs else None
    check(len(body)==views[0][1] and bool(vs) and vs[0]['codec_name']=='h264' and (dims==(1080,1920) and not rot or dims==(1920,1080) and abs(rot or 0)==90),'받은 영상이 줄인 것: h264 %s 회전 %s'%(dims,rot))
    check(len(aus)==1 and aus[0]['codec_name']=='aac','소리(AAC)가 남음')
    ok=pg.evaluate("""(async()=>{const v=[...document.querySelectorAll('video')].find(x=>x.currentSrc||x.src);if(!v)return 'no';v.muted=true;try{await v.play()}catch(e){return 'play:'+e.message};await new Promise(r=>setTimeout(r,800));return v.currentTime>0?'ok':'stuck'})()""")
    check(ok=='ok','줄인 영상이 크게 보기에서 재생됨 ('+ok+')')
    c.close()
    # 2) 줄이기를 못 하는 브라우저: 원본 그대로(큰 건 나눠 올리기)
    c,pg=start(b,'delete window.VideoEncoder; delete window.VideoDecoder;')
    msgs=pick(pg,[BIG])
    sh=[m for m in msgs if '줄이는 중' in m]
    check(len(sh)>0 and all(m.split('|')[0].endswith('· 0%') for m in sh),'줄이기를 못 하면 퍼센트가 오르지 않고 바로')
    puts,_=send(pg,300000)
    check(len([s for s in puts if s[0]=='multipart'])==3,'원본 그대로 나눠 올리기(조각 3개)')
    c.close()
    # 3) 브라우저에 줄이기 기능은 있지만 H.264로 못 만드는 경우: 원본 그대로
    c,pg=start(b,"VideoEncoder.isConfigSupported=async(c)=>({supported:false,config:c});")
    pick(pg,[QHD])
    puts,_=send(pg)
    check([s[1] for s in puts if s[0]=='view']==[os.path.getsize(QHD)],'H.264를 못 만들면 원본 그대로 '+str([s[1] for s in puts if s[0]=='view']))
    c.close()
    b.close()
print('FAILS',FAILS)
