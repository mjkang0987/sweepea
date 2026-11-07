# 178: 앱 출입증(Authorization: Bearer)으로 올리기 API(만들기·넣기·끝내기), 쿠키 흐름은 그대로
import json, base64, os, urllib.request
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=os.path.dirname(os.path.abspath(__file__))+'/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
def call(method,path,token=None,body=None,ctype='application/json'):
    h={}
    if token: h['authorization']='Bearer '+token
    data=None
    if body is not None:
        data=body if isinstance(body,bytes) else json.dumps(body).encode()
        h['content-type']=ctype
    req=urllib.request.Request(B+path,data=data,headers=h,method=method)
    try:
        r=urllib.request.urlopen(req); return r.status,json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e: return e.code,json.loads(e.read() or b'{}')
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(); pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    tok=json.loads(base64.b64decode(next(c['value'] for c in ctx.cookies() if c['name']=='sp_parent').replace('%3D','=')))['access']
    fam=pg.goto(B+'/upload') and pg.locator('#up-form').get_attribute('data-family')
    group=pg.locator('input[name=group]').first.get_attribute('value')
    meta={'familyId':fam,'kind':'photo','takenAt':'2026-11-01T03:00:00Z','takenAtSource':'exif','width':4,'height':3,'groupIds':[group]}
    s,j=call('POST','/api/media',None,meta); check(s==401,'출입증 없으면 401')
    s,j=call('POST','/api/media','bad token!',meta); check(s==401,'토큰 글자 아니면 401')
    s,j=call('POST','/api/media',tok,meta); check(s==201 and 'id' in j,'출입증으로 사진 행 만들기'); mid=j['id']
    img=open(D+'u0.jpg','rb').read()
    s,v=call('PUT',f'/api/media/{mid}/view',tok,img,'image/jpeg'); check(s==201 and v['size']==len(img),'보기 사진 넣기')
    s,t=call('PUT',f'/api/media/{mid}/thumb',tok,img,'image/jpeg'); check(s==201,'썸네일 넣기')
    s,j=call('PUT',f'/api/media/{mid}/thumb','someone-else',img,'image/jpeg'); check(s in (401,404),'남의 출입증은 못 넣음 '+str(s))
    s,j=call('POST',f'/api/media/{mid}/done',tok,{'view':v['key'],'thumb':t['key']}); check(s==200 and j['id']==mid,'끝내기')
    s,j=call('POST','/api/app/media-urls',tok,{'ids':[mid]}); check(s==200 and mid in j['urls'],'올린 사진 주소 받기')
    # 쿠키 흐름(웹 올리기 화면)은 그대로
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u1.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    check(pg.locator('.sp-p__cell').count()==2,'웹 올리기도 그대로(2장)')
    b.close()
