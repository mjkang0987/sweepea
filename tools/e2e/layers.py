# 가운데 레이어: 부모 들어오기 신청, 가족 승인 완료, 가족 새 사진 — 한 번만
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
def upload(pg):
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    upload(pg)
    check(pg.locator('.sp-layer').count()==0,'신청 없으면 레이어 없음')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    def enter(name):
        x=b.new_context(viewport={'width':390,'height':844}); xp=x.new_page(); xp.goto(B+'/i/'+code)
        xp.fill('#who-name',name); xp.get_by_role('button',name='들어가기').click(); xp.wait_for_url('**/password**'); xp.fill('#pw','0917'); xp.get_by_role('button',name='들어가기').click(); xp.wait_for_url('**/wait')
        return x,xp
    g,gp=enter('외할머니')
    pg.goto(B+'/home'); dl=pg.get_by_role('dialog')
    check(dl.count()==1 and '외할머니가 가족 앨범에 들어오려고 해요' in dl.inner_text(),'부모: 들어오기 신청 레이어')
    pg.screenshot(path=D+'ly-join.png')
    pg.get_by_role('button',name='나중에').click(); pg.wait_for_url('**/home')
    check(pg.get_by_role('dialog').count()==0 and pg.locator('.sp-p__alert').count()==1,'나중에 → 레이어 닫히고 띠는 남음')
    pg.reload(); check(pg.get_by_role('dialog').count()==0,'다시 열어도 안 뜸')
    h,hp=enter('큰이모')
    pg.goto(B+'/home'); dl=pg.get_by_role('dialog')
    check(dl.count()==1 and '큰이모' in dl.inner_text() and '2명' in dl.inner_text(),'새 신청이 오면 다시(기다리는 사람 수)')
    pg.get_by_role('button',name='확인하기').click(); pg.wait_for_url('**/settings/family')
    check(True,'확인하기 → 가족 설정')
    pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    # 가족: 승인 뒤 처음
    gp.goto(B+'/album'); dl=gp.get_by_role('dialog')
    check(dl.count()==1 and '엄마아빠가 확인했어요' in dl.inner_text(),'가족: 승인 완료 레이어')
    gp.screenshot(path=D+'ly-ok.png')
    gp.get_by_role('button',name='사진 보기').click(); gp.wait_for_url('**/album**')
    check(gp.get_by_role('dialog').count()==0,'사진 보기 → 닫힘')
    gp.reload(); check(gp.get_by_role('dialog').count()==0,'다시 열어도 안 뜸(지금 사진까지 본 걸로)')
    # 새 사진
    upload(pg); upload(pg)
    gp.goto(B+'/album'); dl=gp.get_by_role('dialog')
    check(dl.count()==1 and '새 사진 2장이 왔어요' in dl.inner_text() and gp.locator('.sp-layer__thumb').count()==2,'가족: 새 사진 2장 레이어')
    gp.screenshot(path=D+'ly-new.png')
    gp.get_by_role('button',name='보기').click(); gp.wait_for_url('**/album**')
    gp.reload(); check(gp.get_by_role('dialog').count()==0,'보기 → 다시 안 뜸')
    # 다른 기기(쿠키 없음)로 처음: 새 사진 레이어 없음
    n=b.new_context(viewport={'width':390,'height':844}); n.add_cookies([x for x in g.cookies() if not x['name'].startswith('sp_photos') and x['name']!='sp_waited']); np=n.new_page()
    np.goto(B+'/album'); check(np.get_by_role('dialog').count()==0,'처음 여는 기기엔 새 사진 레이어 없음')
    upload(pg); np.goto(B+'/album'); check('새 사진 1장' in np.get_by_role('dialog').inner_text(),'그 뒤 올라온 사진은 레이어')
    d=b.new_context(viewport={'width':390,'height':844},color_scheme='dark'); d.add_cookies(n.cookies()); dp=d.new_page(); dp.goto(B+'/album'); dp.screenshot(path=D+'ly-new-dark.png')
    b.close()
from PIL import Image as I
ims=[I.open(D+'ly-'+x+'.png') for x in ('join','ok','new','new-dark')]
o=I.new('RGB',(sum(i.width for i in ims)+30,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(D+'ly-all.png'); print('ALL OK')
