# 주소 복사(사용자 2026-10-29 "길게 눌러도 복사 안 되던데"): 아이폰 사파리는 읽기 전용 칸을 길게 눌러도 복사 메뉴가 안 떠서
# 링크 카드(설정 › 가족, 그룹 화면에 그 자리에서 붙는 카드)에 '주소 복사' 버튼. 복사되면 '주소를 복사했어요', 못 하면 칸을 골라 두기(읽기 전용 풀고 전체 선택) (mock, 인자 webkit)
import sys
from playwright.sync_api import sync_playwright
B='http://localhost:4321'
eng=sys.argv[1] if len(sys.argv)>1 else 'chromium'
fails=[]
def check(c,m): print(('OK ' if c else 'FAIL ')+m); c or fails.append(m)
with sync_playwright() as p:
    br=getattr(p,eng).launch()
    ctx=br.new_context(viewport={'width':390,'height':844})
    if eng=='chromium': ctx.grant_permissions(['clipboard-read','clipboard-write'],origin=B)
    pg=ctx.new_page()
    pg.goto(B+'/login'); pg.get_by_role('link',name='개발용으로 계속하기').click(); pg.wait_for_url('**/setup')
    pg.fill('#child','하린'); pg.fill('#birth','2025-01-03'); pg.get_by_role('button',name='다음').click(); pg.wait_for_url('**/setup/password**')
    pg.fill('#pw','0917'); pg.get_by_role('button',name='시작하기').click(); pg.wait_for_url('**/home')
    pg.goto(B+'/settings/family/groups'); pg.locator('.sp-p__row').first.click(); pg.wait_for_url('**/groups/*')
    pg.get_by_role('button',name='주소 다시 만들기 (예전 주소는 바로 막혀요)').click(); pg.wait_for_selector('#grp-ask[open]')
    pg.locator('#grp-ask').get_by_role('button',name='다시 만들기').click(); pg.wait_for_selector('#link-url')
    btn=pg.get_by_role('button',name='주소 복사')
    check(btn.is_visible(),'링크 카드에 주소 복사 버튼')
    check(pg.locator('label[for=link-url]').inner_text()=='주소','길게 눌러 복사 안내 글 없앰')
    url=pg.locator('#link-url').input_value()
    if eng=='chromium':
        btn.click(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('복사했어요')")
        check(pg.evaluate('navigator.clipboard.readText()')==url,'클립보드에 주소')
        t=pg.locator('.sp-toast'); check(t.count()==1 and t.inner_text()=='주소를 복사했어요.' and t.is_visible(),'복사했어요 토스트가 보임')
    # 복사 못 하는 경우(권한 거절 등): 칸을 골라 두기
    pg.evaluate("navigator.clipboard && (navigator.clipboard.writeText=()=>Promise.reject(new Error('x'))); 0")
    btn.click(); pg.wait_for_function("document.getElementById('as-live')?.textContent.includes('골라 두었어요')")
    sel=pg.evaluate("(()=>{const i=document.getElementById('link-url');return [i.readOnly,document.activeElement===i,i.selectionEnd-i.selectionStart,i.value.length]})()")
    check(sel[0] is False and sel[1] and sel[2]==sel[3],f'못 하면 칸 전체를 골라 둠 {sel}')
    pg.locator('label[for=link-url]').click(); pg.keyboard.press('Tab')
    check(pg.evaluate("document.getElementById('link-url').readOnly"),'칸을 벗어나면 다시 읽기 전용')
    # 스크립트 없이 보낸 경우처럼 설정 › 가족 화면에 바로 뜨는 카드도 버튼이 보임
    gid=pg.url.split('/groups/')[1].split('?')[0]
    pg.goto(B+'/settings/family'); pg.evaluate("(g)=>{const f=document.createElement('form');f.method='post';f.action='/settings/family';const i=document.createElement('input');i.name='do';i.value='share:'+g;f.append(i);document.body.append(f);HTMLFormElement.prototype.submit.call(f)}",gid)
    pg.wait_for_selector('#link-url')
    check(pg.get_by_role('button',name='주소 복사').is_visible(),'설정 › 가족 화면의 카드에도 주소 복사 버튼')
    br.close()
print('FAILS',fails)
