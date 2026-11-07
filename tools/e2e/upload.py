# 올리기 API 검사 (mock 백엔드 + 로컬 R2)
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; F='00000000-0000-4000-8000-00000000f001'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
def enter(b, name, code='Harin001', pw='1234'):
    c=b.new_context(); pg=c.new_page(); pg.goto(B+'/i/'+code)
    pg.get_by_role('button',name=name,exact=True).click(); pg.wait_for_url('**/password**')
    pg.fill('#pw',pw); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    return c,pg
JPG=b'\xff\xd8\xff\xe0'+b'0'*2000
MP4=b'\x00\x00\x00\x18ftypmp42'+b'0'*5000
NEW={'familyId':F,'kind':'photo','takenAt':'2026-10-20T10:00:00Z','takenAtSource':'exif','width':2048,'height':1536}
with sync_playwright() as p:
    b=p.chromium.launch()
    gm,gpg=enter(b,'외할머니'); dad,dpg=enter(b,'하린 아빠')
    gpg.reload(); check('아직 올라온 사진이 없어요' in gpg.content(),'처음엔 0장')
    anon=b.new_context()
    check(anon.request.post(B+'/api/media',data=NEW).status==401,'출입증 없으면 401')
    check(gm.request.post(B+'/api/media',data=NEW).status==403,'올리기 권한 없으면 403')
    check(dad.request.post(B+'/api/media',data={**NEW,'kind':'gif'}).status==400,'형식 틀린 값은 400')
    r=dad.request.post(B+'/api/media',data=NEW); check(r.status==201,'사진 행 만들기'); mid=r.json()['id']
    put=lambda ctx,part,body,t='image/jpeg': ctx.request.put(f'{B}/api/media/{mid}/{part}',data=body,headers={'content-type':t})
    check(put(gm,'view',JPG).status==404,'남의 사진엔 파일 못 넣음')
    check(put(dad,'view',b'<svg/>','image/svg+xml').status==415,'svg는 거부')
    check(put(dad,'poster',JPG).status==404,'사진엔 poster 없음')
    r=put(dad,'view',JPG); check(r.status==201,'보기용 넣기'); kv=r.json()['key']
    r=dad.request.post(f'{B}/api/media/{mid}/done',data={'view':kv}); check(r.status==409 and r.json()['missing']==['thumb'],'썸네일 없으면 완료 안 됨')
    r=dad.request.post(f'{B}/api/media/{mid}/done',data={'view':kv,'thumb':kv}); check(r.status==409,'보기용 키를 썸네일로 속이면 거부')
    kt=put(dad,'thumb',JPG[:500]).json()['key']
    r=dad.request.post(f'{B}/api/media/{mid}/done',data={'view':kv,'thumb':kt}); check(r.status==200 and r.json()['bytes']==len(JPG)+500,'완료, 크기는 서버가 잰 값')
    check(dad.request.post(f'{B}/api/media/{mid}/done',data={'view':kv,'thumb':kt}).status==404,'완료 두 번 안 됨')
    check(put(dad,'view',JPG).status==404,'완료된 사진엔 파일 더 못 넣음')
    gpg.reload(); check(gpg.locator('.sp-a__card').count()==1,'외할머니 앨범에 1장')
    # 영상
    r=dad.request.post(B+'/api/media',data={**NEW,'kind':'video','durationSec':12.5}); vid=r.json()['id']; mid=vid
    check(put(dad,'view',JPG).status==415,'영상 자리에 사진 거부')
    ks={pt:put(dad,pt,body,t).json()['key'] for pt,body,t in (('view',MP4,'video/mp4'),('thumb',JPG,'image/jpeg'),('poster',JPG,'image/jpeg'))}
    check(dad.request.post(f'{B}/api/media/{vid}/done',data=ks).status==200,'영상 완료')
    gpg.reload(); check(gpg.locator('.sp-a__card').count()==2,'외할머니 앨범에 2장')
    # 사진 전달: 서명된 주소
    srcs=[i.get_attribute('src') for i in gpg.locator('.sp-a__card-img').all()]
    check(len(srcs)==2 and all(x.startswith('/m/') for x in srcs),'앨범에 서명된 썸네일 2개')
    r=gm.request.get(B+srcs[0]); check(r.status==200 and r.headers['content-type']=='image/jpeg' and r.headers['x-content-type-options']=='nosniff','썸네일 받기(형식·nosniff)')
    check('private' in r.headers['cache-control'],'캐시는 private')
    r=gm.request.get(B+srcs[0],headers={'range':'bytes=0-99'}); check(r.status==206 and r.headers['content-range'].startswith('bytes 0-99/') and len(r.body())==100,'범위 요청 206')
    full=len(gm.request.get(B+srcs[0]).body())
    r=gm.request.get(B+srcs[0],headers={'range':'bytes=0-99999999'}); check(r.status==206 and r.headers['content-length']==str(full) and len(r.body())==full,'끝을 넘는 범위는 파일 크기로 자름')
    r=gm.request.get(B+srcs[0],headers={'range':'bytes=-99999999'}); check(r.status==206 and r.headers['content-range']==f'bytes 0-{full-1}/{full}','큰 suffix 범위')
    for rg in ('bytes=99999999-','bytes=0-1,5-6'):
        r=gm.request.get(B+srcs[0],headers={'range':rg}); check((r.status in (200,206,416) and (r.status!=206 or r.headers['content-length']==str(len(r.body())))),f'이상한 범위 {rg} → {r.status}')
        path,q=srcs[0].split('?'); e=q.split('&')[0]; sig=q.split('s=')[1]
    check(gm.request.get(B+path+'?'+e+'&s='+('A' if sig[0]!='A' else 'B')+sig[1:]).status==404,'서명 틀리면 404')
    check(gm.request.get(B+path+'?e=1&s='+sig).status==404,'만료면 404')
    other=srcs[1].split('?')[0]
    check(gm.request.get(B+other+'?'+q).status==404,'다른 파일에 서명 재사용 불가')
    check(gm.request.get(B+'/m/../../x?'+q).status==404,'키 형식 아니면 404')
    # 도윤이네만 들어간 기기는 하린이네 사진을 못 봄
    dy,dpg2=enter(b,'할머니','Doyun001','9999'); check('아직 올라온 사진이 없어요' in dpg2.content(),'다른 가족방 사진은 안 보임')
    b.close()
print('ALL OK')
