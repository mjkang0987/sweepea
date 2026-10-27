# 영상 폰에서 줄이기(80): 큰 영상은 1080p로 줄여 한 번에 올리고(진행률 %·화면 켜 두기 안내), 작은 영상과 줄이기를 못 하는 브라우저는 원본 그대로 (mock)
# 준비: 재생되는 130MB 영상(bigvideo.py와 같은 방법, BIG 경로를 인자로 받음)
import os,sys,struct
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
BIG=sys.argv[1] if len(sys.argv)>1 else '/tmp/big.mp4'
if not os.path.exists(BIG):
    with open(BIG,'wb') as f:
        f.write(open(D+'v.mp4','rb').read()); pad=130*1024*1024; f.write(struct.pack('>I',pad+8)+b'free'); f.write(b'\0'*pad)
FAILS=[]
def check(c,msg):
    print('ok' if c else 'FAIL',msg)
    if not c: FAILS.append(msg)
def start(b,init=None):
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    if init: pg.add_init_script(init)
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload')
    return c,pg,None
def pick(pg,files):
    msgs=[]; pg.expose_function('note',lambda t: msgs.append(t))
    pg.evaluate("""new MutationObserver(()=>note(document.getElementById('up-status').textContent+'|'+document.getElementById('up-shrink-hint').hidden+'|'+document.getElementById('up-size').textContent)).observe(document.getElementById('up-status'),{childList:true,characterData:true,subtree:true})""")
    pg.set_input_files('#up-files',files); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=180000)
    return msgs
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1) 큰 영상 + 작은 영상: 큰 것은 줄여서 한 번에, 작은 것은 원본 그대로
    c,pg,_=start(b)
    msgs=pick(pg,[BIG,D+'v.mp4',D+'u0.jpg'])
    check(pg.locator('.sp-p__up-note').inner_text().count('원본은 스위피에 올라가지 않으니')==1,'원본·줄임 안내가 보임')
    pct=[m for m in msgs if m.startswith('영상 줄이는 중… 1 / 3 · ')]
    check(len(pct)>=3 and pct[-1].split('|')[0].endswith('%'),'영상 줄이는 중… 1 / 3 · N% 로 진행률 '+str([m.split('|')[0] for m in pct[:2]]+[pct[-1].split('|')[0]] if pct else []))
    check(all(m.split('|')[1]=='false' and m.split('|')[2]=='줄이는 중' for m in pct),'줄이는 동안 화면 켜 두기 안내·크기 칸 줄이는 중')
    check(pg.locator('#up-bar').is_hidden(),'다 줄이면 진행 막대 숨김')
    check(pg.locator('#up-shrink-hint').is_hidden() and 'MB' in pg.locator('#up-size').inner_text(),'다 줄이면 안내 숨김·크기 보임 ('+pg.locator('#up-size').inner_text()+')')
    mb=float(pg.locator('#up-size').inner_text().split('·')[1].replace('MB',''))
    check(mb<10,'130MB 영상이 작게 줄어듦 (%.1fMB)'%mb)
    bars=[]; pg.expose_function('noteBar',lambda v: bars.append(v))
    pg.evaluate("new MutationObserver(()=>{const b=document.getElementById('up-bar');noteBar((b.hidden?'h':'v')+b.value)}).observe(document.getElementById('up-bar'),{attributes:true})")
    n0=len(msgs); puts=[]; pg.expose_function('notePut',lambda a: puts.append(a))
    pg.evaluate("const g=window.fetch;window.fetch=(u,o)=>{if(o&&o.method==='PUT'&&String(u).includes('/api/media/'))notePut([String(u).split('?')[0].split('/').pop(),o.body?.size??0]);return g(u,o)}")
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=120000)
    up=[m.split('|')[0] for m in msgs[n0:] if m.startswith('올리는 중…')]
    check(any(u.endswith('· 100%') for u in up) and any(u.startswith('올리는 중… 3 / 3 · ') for u in up),'올릴 때도 퍼센트(사진 포함, 마지막 100%) '+str(up[:2]+up[-1:]))
    check(any(x.startswith('v') for x in bars),'올릴 때 진행 막대 보임 '+str(bars[-3:]))
    views=[s for s in puts if s[0]=='view']
    check(not any(s[0]=='multipart' for s in puts),'줄였으니 나눠 올리기 없이 한 번에')
    check(len(views)==3 and max(v[1] for v in views)<10*1024*1024 and any(v[1]==os.path.getsize(D+'v.mp4') for v in views),'작은 영상은 원본 그대로, 큰 영상은 줄인 크기로 '+str([v[1] for v in views]))
    # 앨범에서 줄인 영상이 재생됨(받아 볼 수 있고 mp4)
    pg.locator('.sp-p__cell-link').nth(0).click(); pg.wait_for_url('**/view/**'); pg.wait_for_selector('video')
    ok=pg.evaluate("""(async()=>{const v=[...document.querySelectorAll('video')].find(x=>x.currentSrc||x.src);if(!v)return 'no';v.muted=true;try{await v.play()}catch(e){return 'play:'+e.message};await new Promise(r=>setTimeout(r,800));return v.currentTime>0?'ok':'stuck'})()""")
    check(ok=='ok','줄인 영상이 크게 보기에서 재생됨 ('+ok+')')
    c.close()
    # 2) 줄이기를 못 하는 브라우저: 원본 그대로(큰 건 나눠 올리기)
    c,pg,_=start(b,'delete window.VideoEncoder; delete window.VideoDecoder;')
    msgs=pick(pg,[BIG])
    check(all(m.split('|')[0].endswith('· 0%') for m in msgs if '줄이는 중' in m),'줄이기를 못 하면 영상 퍼센트가 오르지 않고 바로')
    puts=[]; pg.expose_function('notePut',lambda a: puts.append(a))
    pg.evaluate("const g=window.fetch;window.fetch=(u,o)=>{if(o&&o.method==='PUT'&&String(u).includes('/api/media/'))notePut([String(u).split('?')[0].split('/').pop(),o.body?.size??0]);return g(u,o)}")
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=300000)
    check(len([s for s in puts if s[0]=='multipart'])==3,'원본 그대로 나눠 올리기(조각 3개)')
    c.close()
    b.close()
print('FAILS',FAILS)
