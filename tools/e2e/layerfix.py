# 가운데 레이어가 다른 테스트의 클릭을 가리지 않게: 페이지 이동·클릭 뒤 레이어가 있으면 닫는다(레이어 자체는 layers.py가 검사). 확인 레이어(#confirm)는 검사가 직접 누름
from playwright.sync_api import Page
def _dismiss(pg):
    # 그 자리에서 닫히면 다음 레이어가 이어서 뜰 수 있어 몇 번 더(숨겨 둔 레이어는 건너뜀)
    for _ in range(3):
        try:
            sel='.sp-layer:not(#confirm):not([hidden]) form button'
            if not pg.locator(sel).count(): return
            pg.locator(sel).last.click(); pg.wait_for_load_state(); pg.wait_for_timeout(100)
        except Exception: return
_goto=Page.goto; _reload=Page.reload
def goto(self,*a,**k):
    r=_goto(self,*a,**k); _dismiss(self); return r
def reload(self,*a,**k):
    r=_reload(self,*a,**k); _dismiss(self); return r
_wfu=Page.wait_for_url
def wait_for_url(self,*a,**k):
    r=_wfu(self,*a,**k); _dismiss(self); return r
Page.goto=goto; Page.reload=reload; Page.wait_for_url=wait_for_url
