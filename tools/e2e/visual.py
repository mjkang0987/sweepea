# 실제 JPEG를 두 가족방에 올리고 앨범 화면을 찍는다
import io, random
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, "/home/claude/sweepea/tools/e2e"); import layerfix  # noqa
B='http://localhost:4321'; OUT='/home/claude/sweepea/tools/e2e/v-'
H='00000000-0000-4000-8000-00000000f001'; D='00000000-0000-4000-8000-00000000f002'
def enter(b,name,code,pw,scheme='light'):
    c=b.new_context(viewport={'width':390,'height':844},color_scheme=scheme); pg=c.new_page(); pg.goto(B+'/i/'+code)
    pg.get_by_role('button',name=name,exact=True).click(); pg.wait_for_url('**/password**')
    pg.fill('#pw',pw); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    return c,pg
def jpg(w,h,color,label):
    im=Image.new('RGB',(w,h),color); d=ImageDraw.Draw(im); d.ellipse((w*.3,h*.3,w*.7,h*.7),fill=(255,255,255)); d.text((20,20),label,fill=(0,0,0))
    bio=io.BytesIO(); im.save(bio,'JPEG',quality=80); return bio.getvalue()
def up(ctx,fam,day,w,h,color,label):
    r=ctx.request.post(B+'/api/media',data={'familyId':fam,'kind':'photo','takenAt':day,'takenAtSource':'exif','width':w,'height':h}); mid=r.json()['id']
    keys={}
    for part,(pw,ph) in (('view',(w,h)),('thumb',(w//4,h//4))):
        keys[part]=ctx.request.put(f'{B}/api/media/{mid}/{part}',data=jpg(pw,ph,color,label),headers={'content-type':'image/jpeg'}).json()['key']
    assert ctx.request.post(f'{B}/api/media/{mid}/done',data=keys).status==200
random.seed(3)
with sync_playwright() as p:
    b=p.chromium.launch()
    dad,_=enter(b,'하린 아빠','Harin001','1234'); mom,_=enter(b,'도윤 엄마','Doyun001','9999')
    days=['2026-10-21T03:00:00Z','2026-10-21T02:00:00Z','2026-10-14T05:00:00Z','2026-10-03T05:00:00Z']
    for i in range(9):
        w,h=random.choice([(1536,2048),(2048,1536),(1600,1600)])
        up(dad,H,days[i%4],w,h,(random.randint(120,240),random.randint(120,240),random.randint(120,240)),f'H{i}')
    for i in range(3):
        up(mom,D,days[i],1536,2048,(240,200,140),f'D{i}')
    gm,pg=enter(b,'외할머니','Harin001','1234')
    pg.goto(B+'/i/Doyun001'); pg.get_by_role('button',name='할머니',exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','9999'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    pg.wait_for_timeout(300); pg.screenshot(path=OUT+'swipe.png')
    pg.get_by_role('link',name='모아 보기').click(); pg.wait_for_load_state(); pg.wait_for_timeout(300); pg.screenshot(path=OUT+'list.png')
    pg.get_by_role('link',name='작게(한 줄에 더 많이)').click(); pg.get_by_role('link',name='작게(한 줄에 더 많이)').click(); pg.wait_for_load_state(); pg.wait_for_timeout(300); pg.screenshot(path=OUT+'list5.png')
    pg.get_by_role('link',name='도윤이네').click(); pg.wait_for_load_state(); pg.wait_for_timeout(300); pg.screenshot(path=OUT+'doyun.png')
    pg.locator('.sp-a__cell-link').first.click(); pg.wait_for_load_state(); pg.wait_for_timeout(300); pg.screenshot(path=OUT+'detail.png')
    print(pg.url)
    d=b.new_context(viewport={'width':390,'height':844},color_scheme='dark'); dp=d.new_page()
    d.add_cookies(gm.cookies()); dp.goto(B+'/album'); dp.wait_for_timeout(300); dp.screenshot(path=OUT+'swipe-dark.png')
    b.close()
from PIL import Image as I
ims=[I.open(OUT+n+'.png') for n in ('swipe','list','list5','doyun','detail','swipe-dark')]
o=I.new('RGB',(sum(i.width for i in ims)+50,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(OUT+'all.png'); print('ok')
