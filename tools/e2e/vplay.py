# 크게 보기 새 배치: 사진·영상, 재생 → 막대 줄만, 화면 누르면 일시정지, 밀기·‹ ›, 스크립트 끄면 기본 막대
import io, sys, random, time
DAY=time.strftime('2027-%m-%dT%H:%M', time.gmtime(time.time()-random.randint(0,30000000)))
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
H='00000000-0000-4000-8000-00000000f001'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
def enter(b,name,vw=390,vh=844,scheme='light',js=True):
    c=b.new_context(viewport={'width':vw,'height':vh},color_scheme=scheme,java_script_enabled=js,has_touch=True); pg=c.new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name=name,exact=True).click(); pg.wait_for_url('**/password**')
    pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    return c,pg
def jpg(w,h,color):
    im=Image.new('RGB',(w,h),color); d=ImageDraw.Draw(im); d.ellipse((w*.3,h*.3,w*.7,h*.7),fill=(255,255,255))
    bio=io.BytesIO(); im.save(bio,'JPEG',quality=80); return bio.getvalue()
def up(ctx,kind,day,w,h,color,dur=None):
    data={'familyId':H,'kind':kind,'takenAt':day,'takenAtSource':'exif','width':w,'height':h}
    if dur: data['durationSec']=dur
    mid=ctx.request.post(B+'/api/media',data=data).json()['id']; keys={}
    parts=[('view',None),('thumb',None)]+([('poster',None)] if kind=='video' else [])
    for part,_ in parts:
        if kind=='video' and part=='view': body,ct=open(D+'v.mp4','rb').read(),'video/mp4'
        else: body,ct=jpg(w//2,h//2,color),'image/jpeg'
        keys[part]=ctx.request.put(f'{B}/api/media/{mid}/{part}',data=body,headers={'content-type':ct}).json()['key']
    assert ctx.request.post(f'{B}/api/media/{mid}/done',data=keys).status==200
    return mid
with sync_playwright() as p:
    b=p.chromium.launch()
    dad,_=enter(b,'하린 아빠')
    p1=up(dad,'photo',DAY+':05Z',1536,2048,(170,210,240))
    v1=up(dad,'video',DAY+':04Z',720,1280,(0,0,0),6)
    p2=up(dad,'photo',DAY+':03Z',2048,1536,(240,200,140))
    gm,pg=enter(b,'외할머니')
    pg.goto(B+'/album/'+v1); pg.wait_for_load_state()
    check(pg.locator('video').get_attribute('controls') is None,'스크립트가 기본 막대를 끔')
    check(pg.locator('.sp-v__play').is_visible() and pg.locator('.sp-v__ctrl').is_visible(),'재생 버튼·막대 보임')
    check(pg.locator('.sp-v__total').inner_text()=='0:06','길이 0:06')
    check(pg.locator('a[rel="prev"]').count()==1 and pg.locator('a[rel="next"]').count()==1,'‹ › 둘 다')
    pg.screenshot(path=D+'vp-paused.png')
    pg.locator('.sp-v__play').click(); pg.wait_for_timeout(700)
    check(pg.locator('.sp-v').get_attribute('data-playing') is not None,'재생 중 표시')
    check(not pg.locator('.sp-v__bar').is_visible() and not pg.locator('.sp-r').is_visible() and pg.locator('.sp-v__seek').is_visible(),'재생 중엔 막대 줄만')
    t=pg.evaluate("document.querySelector('video').currentTime"); check(t>0,'실제로 재생됨')
    pg.screenshot(path=D+'vp-playing.png')
    pg.locator('.sp-v__mute').click(); pg.wait_for_function("document.querySelector('.sp-v__mute').getAttribute('aria-pressed')==='true'",timeout=3000); check(pg.evaluate("document.querySelector('video').muted") and pg.locator('.sp-v__mute').get_attribute('aria-pressed')=='true','소리 끄기(눌림)')
    pg.locator('.sp-v__seek').fill('4'); check(abs(pg.evaluate("document.querySelector('video').currentTime")-4)<0.5,'막대로 4초로')
    check(pg.url.endswith(v1),'막대 조작으로 넘어가지 않음')
    pg.mouse.click(195,300); pg.wait_for_timeout(300)
    check(pg.locator('.sp-v').get_attribute('data-playing') is None and pg.evaluate("document.querySelector('video').paused"),'화면 누르면 일시정지')
    check(pg.locator('.sp-v__bar').is_visible() and pg.locator('.sp-r').is_visible(),'메뉴 다시 보임')
    # 밀기(터치): 왼쪽으로 밀면 다음
    pg.evaluate("""()=>{const v=document.querySelector('[data-v]');const o={pointerId:1,pointerType:'touch',isPrimary:true,bubbles:true};
      document.querySelector('.sp-v__stage').dispatchEvent(new PointerEvent('pointerdown',{...o,clientX:300,clientY:300}));
      document.querySelector('.sp-v__stage').dispatchEvent(new PointerEvent('pointerup',{...o,clientX:120,clientY:310}));}""")
    pg.wait_for_url('**/album/'+p2+'**'); check(True,'왼쪽으로 밀면 다음')
    check(pg.locator('.sp-v__ctrl').count()==0 and pg.locator('img.sp-v__media').count()>=1,'사진은 막대 없음(스와이퍼면 슬라이드마다 사진)')
    check(pg.locator('.sp-r__btn').first.get_attribute('aria-label').startswith('하트') and pg.locator('.sp-r__label').count()==0,'반응은 이모지만, 이름은 화면 읽기용')
    pg.screenshot(path=D+'vp-photo.png')
    pg.locator('a[rel="prev"]').click(); pg.wait_for_url('**/album/'+v1+'**'); check(True,'‹ 누르면 이전')
    # 한마디
    pg.fill('#say-body','잘 봤다'); pg.get_by_role('button',name='보내기').click(); pg.wait_for_load_state()
    check('보냈어요' in pg.locator('.sp-toast').inner_text() and pg.locator('.sp-toast').get_attribute('role')=='status','한마디 보냄 토스트')
    # 넘겨 보기 한마디 칸
    pg.goto(B+'/album'); pg.wait_for_load_state()
    check(pg.get_by_text('직접 쓰기').count()==0 and pg.locator('.sp-a__slide .sp-say').count()>=3,'넘겨 보기 카드마다 한마디 칸')
    say1=pg.locator('.sp-a__slide').first.locator('.sp-say')  # 카드 한마디 폼(id 끝은 사진 id)
    say1.locator('input[name=body]').fill('넘겨서 한마디'); say1.get_by_role('button',name='보내기').click(); pg.wait_for_load_state()
    say1=pg.locator('.sp-a__slide').first.locator('.sp-say')
    check(pg.locator('.sp-toast').count()==1 and '보냈어요' in pg.locator('.sp-toast').inner_text() and '보냈어요' not in say1.inner_text(),'결과는 화면 아래 토스트 하나(카드 안 상자 없음)')
    pg.screenshot(path=D+'vp-swipe.png')
    # PC·다크
    c2=b.new_context(viewport={'width':1280,'height':800},color_scheme='dark'); c2.add_cookies(gm.cookies()); q=c2.new_page()
    q.goto(B+'/album/'+v1); q.wait_for_timeout(300); q.screenshot(path=D+'vp-pc.png')
    # 스크립트 없음
    c3=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); c3.add_cookies(gm.cookies()); n=c3.new_page()
    n.goto(B+'/album/'+v1)
    check(n.locator('video').get_attribute('controls') is not None and not n.locator('.sp-v__play').is_visible() and not n.locator('.sp-v__ctrl').is_visible(),'스크립트 없으면 기본 막대')
    n.screenshot(path=D+'vp-nojs.png')
    b.close()
from PIL import Image as I
ims=[I.open(D+'vp-'+n+'.png') for n in ('paused','playing','photo','swipe','nojs')]
o=I.new('RGB',(sum(i.width for i in ims)+40,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(D+'vp-all.png'); print('ALL OK')
