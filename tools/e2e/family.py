# 설정 > 가족: 링크 → 새 이름 → 승인/거절 → 문자 링크 (mock)
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; O='/home/claude/sweepea/tools/e2e/f-'
def check(c,msg):
    if not c: raise SystemExit('FAIL '+msg)
    print('ok',msg)
shots=[]
def newname(b, code, name):
    c=b.new_context(viewport={'width':390,'height':844}); g=c.new_page(); g.goto(B+'/i/'+code)
    g.fill('#who-name',name); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/password**')
    g.fill('#pw','0917'); g.get_by_role('button',name='들어가기').click(); g.wait_for_url('**/wait')
    return c,g
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page()
    def shot(n): pg.screenshot(path=O+n+'.png',full_page=True); shots.append(O+n+'.png')
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','서아'); pg.fill('#birth','2025-09-17'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.fill('#hint','생일'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.get_by_role('link',name='설정').click(); pg.wait_for_url('**/settings')
    pg.get_by_role('link',name='가족').first.click(); pg.wait_for_url('**/settings/family')
    check('지금은 없어요' in pg.content(),'처음엔 승인 대기 없음')
    pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    url=pg.locator('#link-url').input_value(); code=url.rsplit('/',1)[1]
    check(len(code)==8 and pg.get_by_role('link',name='문자로 보내기').get_attribute('href').startswith('sms:?&body='),'링크 만들고 문자 보내기 버튼'); shot('1')
    gm,g=newname(b,code,'외할머니'); check('들어오는 중' in g.content(),'외할머니 새 이름으로 승인 대기')
    au,a2=newname(b,code,'모르는사람')
    pg.goto(B+'/settings'); check('승인 2' in pg.content(),'설정에 승인 2 배지')
    pg.goto(B+'/settings/family'); shot('2')
    pg.get_by_role('button',name='승인 외할머니').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    check('승인했어요' in pg.content(),'승인 안내')
    g.goto(B+'/wait'); check(g.url.endswith('/album'),'승인되면 외할머니 앨범 열림')
    pg.get_by_role('button',name='거절 모르는사람').click(); pg.wait_for_selector('#fam-ask[open]')
    check(pg.locator('#ask-t').inner_text()=='모르는사람 거절할까요?','거절은 한 번 더 확인(레이어)'); shot('2b')
    pg.locator('#fam-ask').get_by_role('button',name='거절').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('처리했어요')")
    r=c.request.post(B+'/settings/family',form={'do':'member:'+'0'*8+'-0000-0000-0000-'+'0'*12+':active'},max_redirects=0)
    check('done=gone' in r.headers['location'],'없는(이미 처리된) 대상은 이미 처리됐다고 안내')
    a2.goto(B+'/wait'); check('이 휴대폰으로는 볼 수 없어요' in a2.content(),'거절된 기기는 막힘')
    pg.get_by_role('link',name='문자로 공유하기').click(); pg.wait_for_url('**/sms')
    check(pg.get_by_label('외할머니').is_checked() if pg.get_by_label('외할머니').count() else False,'등록된 이름 고르기')
    pg.get_by_role('button',name='링크 만들기').click(); pg.wait_for_load_state()
    check("외할머니, 서아 사진 바로 보시게" in pg.content() and pg.get_by_role('link',name='문자로 공유하기').count()==1,'문자 미리보기와 보내기'); shot('3')
    # 다른 부모는 남의 가족 처리 못 함
    b.close()
from PIL import Image
ims=[Image.open(x) for x in shots]; h=max(i.height for i in ims)
o=Image.new('RGB',(sum(i.width for i in ims)+10*len(ims),h),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(O+'all.png'); print('ALL OK')
