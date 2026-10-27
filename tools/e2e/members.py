# 구성원 상세(올리기 허용·내보내기), 가족도 사진 저장하기, 저장 용량
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, "/home/claude/sweepea/tools/e2e"); import layerfix  # noqa
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
shots=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    def shot(n): pg.screenshot(path=D+'m-'+n+'.png',full_page=True); shots.append(D+'m-'+n+'.png')
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=30000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home',timeout=30000)
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=b.new_context(viewport={'width':390,'height':844}); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','서아 아빠'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 서아 아빠').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    pg.get_by_role('link',name='서아 아빠').click(); pg.wait_for_url('**/member/**')
    sw=pg.get_by_role('switch',name='사진 올리기 허용'); check(sw.get_attribute('aria-checked')=='false','처음엔 올리기 꺼짐'); shot('1')
    fam=gp.evaluate("1") and None
    r=g.request.post(B+'/api/media',data={'familyId':pg.locator('#up-form').count() and '' or '00000000-0000-4000-8000-000000000000','kind':'photo','takenAt':'2026-10-20T10:00:00Z','takenAtSource':'exif'})
    sw.click(); pg.wait_for_url('**done=upload-on**'); check(pg.get_by_role('switch',name='사진 올리기 허용').get_attribute('aria-checked')=='true','올리기 켬')
    pg.goto(B+'/settings/family'); check(pg.locator('.sp-p__tag',has_text='올리기').count()==1,'가족 목록에 올리기 표시')
    # 사진 저장하기
    pg.goto(B+'/settings'); dsw=pg.get_by_role('switch',name='가족도 사진 저장하기'); check(dsw.get_attribute('aria-checked')=='false','저장하기 처음엔 꺼짐')
    gp.goto(B+'/album'); gp.locator('.sp-a__card-link').first.click(); gp.wait_for_load_state()
    check(gp.get_by_role('link',name='저장').count()==0,'꺼져 있으면 가족 화면에 저장 없음')
    dsw.click(); pg.wait_for_url('**done=download-on**'); shot('2')
    gp.reload(); check(gp.locator('a.sp-v__link[download]').count()==1,'켜면 가족 크게 보기에 저장 링크')
    pg.goto(B+'/settings/storage'); check('사진 1장' in pg.content() and pg.locator('meter').count()==1,'저장 용량 화면'); shot('3')
    # 내보내기
    pg.goto(B+'/settings/family'); pg.get_by_role('link',name='서아 아빠').click(); pg.wait_for_url('**/member/**')
    pg.get_by_role('button',name='내 가족 아님 · 내보내기 서아 아빠').click(); pg.wait_for_url('**confirm=**')
    check('서아 아빠 내보낼까요?' in pg.content(),'내보내기도 한 번 더 확인')
    check((pg.locator('#fam-ask').get_attribute('data-cancel') or '').startswith('/settings/family/member/'),'취소하면 구성원 화면으로')
    pg.locator('#fam-ask').get_by_role('button',name='내보내기').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('처리했어요')")
    gp.goto(B+'/album'); check('이 휴대폰으로는 볼 수 없어요' in gp.content() or gp.url.endswith('/wait'),'내보낸 사람은 못 봄')
    b.close()
from PIL import Image
ims=[Image.open(x) for x in shots]; h=max(i.height for i in ims)
o=Image.new('RGB',(sum(i.width for i in ims)+30,h),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(D+'m-all.png'); print('ALL OK')
