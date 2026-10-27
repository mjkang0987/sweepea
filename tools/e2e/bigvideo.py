# 큰 영상 나눠 올리기(79): 100MB 넘는 영상도 50MB 조각으로 올라가고, 용량에 잡히고, 크게 보기에서 재생된다. 나눠 올리기 API의 거절도 (mock)
# 준비: 재생되는 130MB 영상이 필요 → 아래처럼 v.mp4 뒤에 mp4 'free' 상자를 붙여 만든다(BIG 경로를 인자로 받음)
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
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login/dev'); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[BIG,D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=120000)
    check('올릴 수 없어요' not in pg.locator('#up-status').inner_text(),'130MB 영상도 고를 수 있음(전엔 100MB에서 빠짐)')
    seen=[]; pg.on('request',lambda r: seen.append((r.method,r.url.split('?')[0].rsplit('/',1)[-1])) if '/api/media/' in r.url else None)
    msgs=[]; pg.expose_function('note',lambda t: msgs.append(t))
    pg.evaluate("new MutationObserver(()=>note(document.getElementById('up-status').textContent)).observe(document.getElementById('up-status'),{childList:true,characterData:true,subtree:true})")
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=300000)
    parts=[s for s in seen if s==('PUT','multipart')]
    check(len(parts)==3,'130MB → 조각 3개로 보냄 (%d)'%len(parts))
    check(any('영상 ' in m and '%' in m for m in msgs),'올리는 중 영상 몇 퍼센트 보여 줌 '+str([m for m in msgs if '%' in m][:3]))
    check(pg.locator('.sp-p__cell-link').count()==2,'영상·사진 둘 다 앨범에')
    pg.goto(B+'/settings/storage'); txt=pg.locator('main').inner_text()
    check('130MB' in txt or '131MB' in txt,'용량에 영상 크기가 잡힘')
    # 크게 보기에서 재생되는지(영상 주소가 끝까지 받아짐)
    pg.goto(B+'/home'); pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**')
    src=pg.evaluate("document.querySelector('video')?.currentSrc||document.querySelector('video')?.src||''")
    r=c.request.get(src,headers={'range':'bytes=0-99'}) if src else None
    check(r is not None and r.status==206,'합친 영상을 받아 볼 수 있음(Range)')
    # 나눠 올리기 API 거절
    mid=pg.url.split('/view/')[1].split('?')[0]
    rr=c.request.post(B+f'/api/media/{mid}/multipart',data={'action':'create','type':'video/mp4','size':10},headers={'origin':B})
    check(rr.status==404,'끝난 사진엔 나눠 올리기 못 함')
    q=c.request.post(B+'/api/media',data={'familyId':pg.evaluate("fetch('/upload').then(r=>r.text()).then(t=>t.match(/data-family=\"([^\"]+)/)[1])"),'kind':'video','takenAt':'2026-01-01T00:00:00Z','takenAtSource':'file','width':10,'height':10},headers={'origin':B})
    nid=q.json()['id']
    big=c.request.post(B+f'/api/media/{nid}/multipart',data={'action':'create','type':'video/mp4','size':3*1024**3},headers={'origin':B})
    check(big.status==413,'2GB 넘으면 거절')
    bad=c.request.post(B+f'/api/media/{nid}/multipart',data={'action':'create','type':'image/png','size':10},headers={'origin':B})
    check(bad.status==415,'영상이 아닌 형식 거절')
    ok=c.request.post(B+f'/api/media/{nid}/multipart',data={'action':'create','type':'video/mp4','size':10},headers={'origin':B}).json()
    other=c.request.put(B+f"/api/media/{nid}/multipart?key=x/{nid}/view-00000000-0000-4000-8000-000000000000&upload={ok['uploadId']}&n=1",data=b'abc',headers={'origin':B,'content-type':'application/octet-stream'})
    check(other.status==400,'다른 사진 키로는 조각 못 넣음')
    toolong=c.request.put(B+f"/api/media/{nid}/multipart?key={ok['key']}&upload={ok['uploadId']}&n=1",data=b'\0'*(50*1024*1024+1),headers={'origin':B,'content-type':'application/octet-stream'})
    check(toolong.status==413,'50MB 넘는 조각 거절')
    order=c.request.post(B+f'/api/media/{nid}/multipart',data={'action':'complete','key':ok['key'],'uploadId':ok['uploadId'],'parts':[{'partNumber':2,'etag':'x'}]},headers={'origin':B})
    check(order.status==400,'조각 번호가 1부터 아니면 거절')
    c.request.post(B+f'/api/media/{nid}/multipart',data={'action':'abort','key':ok['key'],'uploadId':ok['uploadId']},headers={'origin':B})
    b.close()
print('FAILS',FAILS)
