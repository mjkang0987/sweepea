# 가족 캐릭터(110): 가족은 앨범 '내 캐릭터' → /me/avatar, 엄빠는 설정 맨 위 내 이름 줄 → /settings/avatar.
# 고른 그림이 누구세요(다른 기기)·한마디 목록·설정 › 가족·구성원 상세·설정 맨 위에 보이고, '고르지 않음'이면 원래 모양. 고르기는 스크립트 없이(폼)
import sys; sys.path.insert(0, "/home/claude/sweepea/tools/e2e"); import layerfix  # noqa
from playwright.sync_api import sync_playwright
B='http://localhost:4321'; D='/home/claude/sweepea/tools/e2e/'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
def size(loc):
    bb=loc.bounding_box(); return round(bb['width']) if bb else 0
with sync_playwright() as p:
    b=p.chromium.launch()
    # 페이지 전환(@view-transition) 중엔 클릭이 html에 막혀서 움직임 줄이기로(전환 바로 끝남)
    def ctx(js=True, **k): return b.new_context(viewport={'width':390,'height':844}, java_script_enabled=js, reduced_motion='reduce', **k)
    # 1) 하린이네(mock 링크): 외할아버지가 스크립트 없이 캐릭터 고르기 → 다른 기기 누구세요에 보임 → 고르지 않음으로 되돌림
    g=ctx(False); gp=g.new_page()
    gp.goto(B+'/i/Harin001'); gp.get_by_role('button',name='외할아버지').click(); gp.wait_for_url('**/password**')
    gp.fill('#pw','1234'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/album**')
    pill=gp.get_by_role('link',name='내 캐릭터'); check(pill.count()==1,'앨범 머리에 내 캐릭터 알약')
    pill.click(); gp.wait_for_url('**/me/avatar**')
    check(gp.get_by_role('heading',name='내 캐릭터 고르기').is_visible(),'고르기 화면 제목')
    check(gp.get_by_role('group',name='내 캐릭터').count()==1 and gp.locator('input[type=radio][name=avatar]').count()==46,'fieldset 하나에 라디오 46개(고르지 않음 + 45)')
    check(gp.get_by_role('radio',name='고르지 않음',exact=True).is_checked(),'처음엔 고르지 않음')
    check(gp.locator('.sp-av__face--none').inner_text()=='외','고르지 않음 칸은 이름 첫 글자')
    check(gp.get_by_role('radio',name='캐릭터 45',exact=True).count()==1,'라디오마다 이름(캐릭터 N)')
    bar=gp.locator('.sp-f__bottom--fixed'); check(bar.evaluate("e=>getComputedStyle(e).position")=='fixed' and bar.evaluate("e=>getComputedStyle(e).borderTopWidth")=='0px','저장은 아래 고정 막대(위 선 없음)')
    gp.get_by_role('radio',name='캐릭터 7',exact=True).check(); gp.get_by_role('button',name='저장').click(); gp.wait_for_url('**done=saved**')
    check('캐릭터를 저장했어요' in gp.locator('.sp-toast').inner_text(),'저장 토스트(PRG)')
    check(gp.get_by_role('radio',name='캐릭터 7',exact=True).is_checked(),'다시 열면 고른 것이 골라져 있음')
    gp.screenshot(path=D+'av-1-pick.png')
    gp.goto(B+'/album'); check(gp.locator('.sp-a__me img[src="/avatar/7.webp"]').count()==1,'앨범 알약에 내 그림')
    o=ctx(); op=o.new_page(); op.goto(B+'/i/Harin001')
    btn=op.get_by_role('button',name='외할아버지'); img=btn.locator('img')
    check(img.count()==1 and img.get_attribute('src')=='/avatar/7.webp' and img.get_attribute('alt')=='','다른 기기 누구세요: 이름 왼쪽에 그림(alt 빈칸)')
    rem=op.evaluate("parseFloat(getComputedStyle(document.documentElement).fontSize)")
    check(abs(size(img)-2.5*rem)<=1,'누구세요 그림 2.5rem(글자 크게 40px, 글자 크기 따라 커짐: %dpx)'%size(img))
    check(op.get_by_role('button',name='외할머니').locator('img').count()==0,'고르지 않은 사람은 그대로')
    op.screenshot(path=D+'av-2-who.png')
    gp.goto(B+'/me/avatar'); gp.get_by_role('radio',name='고르지 않음',exact=True).check(); gp.get_by_role('button',name='저장').click(); gp.wait_for_url('**done=saved**')
    op.reload(); check(op.get_by_role('button',name='외할아버지').locator('img').count()==0,'고르지 않음으로 되돌리면 누구세요도 원래대로')
    gp.goto(B+'/album'); check(gp.locator('.sp-a__me img').count()==0,'되돌리면 알약도 글자만')
    o.close(); g.close()

    # 2) 새 가족방: 엄빠가 사진 올리고 가족 들이기 → 가족·엄빠 각자 고르기 → 한마디 목록·설정에 보임
    pg=ctx().new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/upload'); pg.set_input_files('#up-files',[D+'u0.jpg']); pg.wait_for_function("!document.querySelector('#up-actions button').disabled",timeout=60000)
    pg.get_by_role('button',name='보내지 않고 올리기만').click(); pg.wait_for_url('**/home**',timeout=60000)
    pg.locator('.sp-p__cell-link').first.click(); pg.wait_for_url('**/view/**'); vid=pg.url.split('/view/')[1].split('?')[0]
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='링크 만들기 (가족)').click(); pg.wait_for_selector('#link-url')
    code=pg.locator('#link-url').input_value().rsplit('/',1)[1]
    g=ctx(False); gp=g.new_page(); gp.goto(B+'/i/'+code)
    gp.fill('#who-name','외할아버지'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/password**'); gp.fill('#pw','0917'); gp.get_by_role('button',name='들어가기').click(); gp.wait_for_url('**/wait')
    gp.goto(B+'/me/avatar'); check(gp.url.endswith('/wait'),'승인 전엔 고르기 화면 대신 대기')
    pg.goto(B+'/settings/family'); pg.get_by_role('button',name='승인 외할아버지').click(); pg.wait_for_function("document.getElementById('fam-live')?.textContent.includes('승인했어요')")
    gp.goto(B+'/album'); gp.get_by_role('link',name='내 캐릭터').click(); gp.wait_for_url('**/me/avatar**')
    gp.get_by_role('radio',name='캐릭터 24',exact=True).check(); gp.get_by_role('button',name='저장').click(); gp.wait_for_url('**done=saved**')
    # 가족 한마디(스크립트 없이 폼)
    gp.goto(B+'/album/'+vid); gp.fill('#say-body','아이고 많이 컸네'); gp.locator('#say').get_by_role('button',name='보내기').click(); gp.wait_for_load_state()
    # 엄빠: 설정 맨 위 내 이름 줄 → 스크립트 없이 고르기
    pn=ctx(False, storage_state=pg.context.storage_state()); pp=pn.new_page()
    pp.goto(B+'/settings'); row=pp.get_by_role('link',name='하린 엄마 내 캐릭터')
    check(row.count()==1 and row.locator('.sp-p__avatar').inner_text()=='엄','설정 맨 위 내 이름 줄(고르기 전엔 첫 글자)')
    row.click(); pp.wait_for_url('**/settings/avatar')
    check(pp.get_by_role('heading',name='내 캐릭터').is_visible() and pp.locator('input[type=radio][name=avatar]').count()==46,'엄빠 고르기 화면')
    sb=pp.locator('.sp-p__savebar'); check(sb.evaluate("e=>getComputedStyle(e).borderTopWidth")=='0px','엄빠 저장 막대 위 선 없음')
    pp.get_by_role('radio',name='캐릭터 1',exact=True).check(); pp.get_by_role('button',name='저장').click(); pp.wait_for_url('**done=saved**')
    check('캐릭터를 저장했어요' in pp.locator('.sp-toast').inner_text(),'엄빠 저장 토스트')
    pp.screenshot(path=D+'av-3-parent.png')
    pp.goto(B+'/settings'); check(pp.get_by_role('link',name='하린 엄마 내 캐릭터').locator('img[src="/avatar/1.webp"]').count()==1,'설정 맨 위에 내 그림')
    # 엄빠 한마디
    pg.goto(B+'/view/'+vid); pg.fill('#say-body','할아버지 보고 싶대요'); pg.locator('#say').get_by_role('button',name='보내기').click(); pg.wait_for_function("!document.querySelector('.sp-v__more[aria-busy]')")
    # 한마디 목록(가족 화면, 스크립트 없이): 쓴 사람 이름 왼쪽 32px
    gp.goto(B+'/album/'+vid+'#talk')
    items=gp.locator('.sp-v__sheet-item')
    fam_img=items.filter(has_text='외할아버지').locator('img'); par_img=items.filter(has_text='할아버지 보고 싶대요').locator('img')
    check(fam_img.get_attribute('src')=='/avatar/24.webp' and fam_img.get_attribute('alt')=='','한마디 목록에 가족 그림')
    check(par_img.get_attribute('src')=='/avatar/1.webp','한마디 목록에 엄빠 그림')
    check(size(fam_img)==32,'한마디 그림 32px')
    gp.screenshot(path=D+'av-4-comments.png')
    # 설정 › 가족 목록·구성원 상세
    pp.goto(B+'/settings/family'); mem=pp.get_by_role('link',name='외할아버지')
    check(mem.locator('img[src="/avatar/24.webp"]').count()==1 and size(mem.locator('img'))==32,'설정 › 가족 줄에 그림')
    mem.click(); pp.wait_for_url('**/member/**'); check(pp.locator('img.sp-avatar[src="/avatar/24.webp"]').count()==1,'구성원 상세에 그림')
    # 엄빠 고르지 않음으로
    pp.goto(B+'/settings/avatar'); pp.get_by_role('radio',name='고르지 않음',exact=True).check(); pp.get_by_role('button',name='저장').click(); pp.wait_for_url('**done=saved**')
    pp.goto(B+'/settings'); check(pp.get_by_role('link',name='하린 엄마 내 캐릭터').locator('img').count()==0,'되돌리면 설정은 첫 글자')
    gp.reload(); check(gp.locator('.sp-v__sheet-item').filter(has_text='할아버지 보고 싶대요').locator('img').count()==0,'되돌리면 한마디 목록도 원래대로')
    # 잘못된 값은 저장 안 함
    r=pp.request.post(B+'/settings/avatar',form={'avatar':'99'},max_redirects=0); check(r.status==303 and 'done=error' in r.headers.get('location',''),'범위 밖 값은 거절')
    b.close()
print('FAILS',fails)
