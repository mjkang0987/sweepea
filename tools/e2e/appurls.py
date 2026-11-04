# 177: 앱용 사진 주소 API
import json, base64, urllib.request, sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D=__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
def post(body,token=None,raw=None):
    h={'content-type':'application/json'}
    if token: h['authorization']='Bearer '+token
    req=urllib.request.Request(B+'/api/app/media-urls',data=raw if raw is not None else json.dumps(body).encode(),headers=h,method='POST')
    try:
        r=urllib.request.urlopen(req); return r.status,json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code,json.loads(e.read() or b'{}')
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844}); pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-09-17'); pg.check('input[name=agree_terms]'); pg.check('input[name=agree_privacy]'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    pg.goto(B+'/home?v=list&z=3')
    mid=pg.locator('.sp-p__cell').first.get_attribute('id')[2:]
    tok=json.loads(base64.b64decode(next(c['value'] for c in ctx.cookies() if c['name']=='sp_parent').replace('%3D','=')))['access']
    s,j=post({'ids':[mid]}); check(s==401,'출입증 없으면 401')
    s,j=post({'ids':['x']},tok); check(s==400,'id 형식 틀리면 400')
    s,j=post({'ids':[]},tok); check(s==400,'빈 목록 400')
    s,j=post(None,tok,raw=b'nope'); check(s==400,'JSON 아니면 400')
    other='00000000-0000-4000-8000-000000000000'
    s,j=post({'ids':[mid,other,mid]},tok); check(s==200 and list(j['urls'])==[mid],'볼 수 있는 사진만, 겹친 id 한 번 '+str(list(j['urls'])))
    u=j['urls'][mid]; check(u['thumb'].startswith(B+'/m/') and u['view'].startswith(B+'/m/') and u['poster'] is None,'절대 주소, 사진은 poster 없음')
    r=urllib.request.urlopen(u['thumb']); check(r.status==200 and r.headers['content-type'].startswith('image/'),'받은 주소로 그림이 열림')
    s,j=post({'ids':[mid]},'not-a-session'); check(s in (200,401) and (s==401 or j['urls']=={}),'모르는 출입증은 사진 없음 '+str(s))
    b.close()
