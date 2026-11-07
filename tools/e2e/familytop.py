# 160: 조부모 앨범 위 줄 줄이기 — 사진 종류는 모아 보기에만, 내 캐릭터·글자 크기는 넘겨 보기 맨 아래·모아 보기 위 (mock)
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; F='00000000-0000-4000-8000-00000000f001'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
def enter(b, name, pw='1234'):
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name=name,exact=True).click(); pg.wait_for_url('**/password**')
    pg.fill('#pw',pw); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    return c,pg
JPG=b'\xff\xd8\xff\xe0'+b'0'*2000
MP4=b'\x00\x00\x00\x18ftypmp42'+b'0'*5000
def add(ctx, kind):
    r=ctx.request.post(B+'/api/media',data={'familyId':F,'kind':kind,'takenAt':'2026-10-20T10:00:00Z','takenAtSource':'exif','width':2048,'height':1536,**({'durationSec':5} if kind=='video' else {})})
    mid=r.json()['id']; put=lambda part,body,t: ctx.request.put(f'{B}/api/media/{mid}/{part}',data=body,headers={'content-type':t}).json()['key']
    ks={'view':put('view',MP4,'video/mp4') if kind=='video' else put('view',JPG,'image/jpeg'),'thumb':put('thumb',JPG,'image/jpeg')}
    if kind=='video': ks['poster']=put('poster',JPG,'image/jpeg')
    check(ctx.request.post(f'{B}/api/media/{mid}/done',data=ks).status==200,f'{kind} 올림')
with sync_playwright() as p:
    b=p.chromium.launch()
    gm,g=enter(b,'외할머니')
    # 사진 없을 때도 맨 아래에서 글자 크기를 바꿀 수 있음
    g.goto(B+'/album?v=swipe')
    if g.locator('.sp-a__card').count()==0:
        check(g.locator('.sp-a__mine').get_by_role('link',name='글자 크기').count()==1,'사진 없을 때도 글자 크기 링크')
    else: print('skip 사진 없을 때 검사(앞선 검사가 이 가족에 사진을 올려 둠)')
    dad,_=enter(b,'하린 아빠'); add(dad,'photo'); add(dad,'video')
    g.goto(B+'/album?v=swipe')
    check(g.get_by_role('navigation',name='사진 종류').count()==0,'넘겨 보기엔 사진 종류 줄 없음')
    # 위 줄은 머리 + 보기 방식뿐: 알약 줄이 사진(넘겨 보기 목록) 뒤에 있음
    order=g.evaluate("(()=>{const m=document.querySelector('.sp-a__mine'),s=document.querySelector('.sp-a__swipe');return !!(m&&s&&(s.compareDocumentPosition(m)&Node.DOCUMENT_POSITION_FOLLOWING))})()")
    check(order and g.locator('.sp-a__mine').count()==1,'넘겨 보기: 내 캐릭터·글자 크기는 사진 아래 하나')
    check(g.locator('.sp-a__mine').get_by_role('link',name='글자 크기').get_attribute('href')=='/me/text-size','글자 크기 링크 그대로')
    check(g.locator('.sp-a__mine').get_by_role('link',name='내 캐릭터').count()==1,'내 캐릭터 링크 그대로')
    check(g.get_by_role('navigation',name='내 설정').count()==1,'내 설정 영역(화면 읽기 영역 목록)')
    # 옛 주소(넘겨 보기 + 영상만)는 걸러지지 않음(줄이 없으니)
    n_all=g.locator('.sp-a__slide').count()
    g.goto(B+'/album?v=swipe&t=video'); check(g.locator('.sp-a__slide').count()==n_all and n_all>=2,'넘겨 보기는 t를 무시하고 전체')
    check('영상' not in g.title(),'넘겨 보기 제목은 사진(영상 아님): '+g.title())
    # 모아 보기는 사진 종류 줄이 있고 거름
    g.goto(B+'/album?v=list'); n_list=g.locator('.sp-a__cell').count()
    check(g.get_by_role('navigation',name='사진 종류').count()==1,'모아 보기엔 사진 종류 줄')
    # 새 사진 레이어가 떠 있을 수 있어 링크 주소로 이동(레이어는 layers.py가 따로 봄)
    g.goto(B+g.get_by_role('navigation',name='사진 종류').get_by_role('link',name='영상').get_attribute('href')); check('t=video' in g.url,'영상 탭 주소')
    nv=g.locator('.sp-a__cell').count(); check(0<nv<n_list,f'모아 보기 영상만 {nv}개(전체 {n_list})')
    order=g.evaluate("(()=>{const ms=document.querySelectorAll('.sp-a__mine'),a=document.querySelector('[data-album]'),z=document.querySelector('.sp-a__zoom-space');return ms.length===1&&!!(a&&z&&(ms[0].compareDocumentPosition(a)&4)&&(a.compareDocumentPosition(z)&4))})()")
    check(order,'모아 보기: 내 캐릭터·글자 크기는 위(목록 앞) 하나, 떠 있는 버튼 자리는 목록 뒤')
    # 모아 보기(영상)에서 넘겨 보기로 가면 전체
    g.goto(B+g.get_by_role('navigation',name='보기 방식').get_by_role('link',name='넘겨 보기').get_attribute('href')); check('v=swipe' in g.url,'넘겨 보기 탭 주소')
    check(g.locator('.sp-a__slide').count()==n_all,'모아 보기에서 영상 고른 뒤 넘겨 보기는 전체')
    b.close()
print('FAILS []')
