# 가운데 레이어가 다른 테스트의 클릭을 가리지 않게: 페이지 이동·클릭 뒤 레이어가 있으면 닫는다(레이어 자체는 layers.py가 검사). 확인 레이어(#confirm)는 검사가 직접 누름
from playwright.sync_api import Page
def _dismiss(pg):
    try:
        if pg.locator('.sp-layer:not(#confirm) form button').count():
            pg.locator('.sp-layer:not(#confirm) form button').last.click(); pg.wait_for_load_state()
    except Exception: pass
_goto=Page.goto; _reload=Page.reload
def goto(self,*a,**k):
    r=_goto(self,*a,**k); _dismiss(self); return r
def reload(self,*a,**k):
    r=_reload(self,*a,**k); _dismiss(self); return r
_wfu=Page.wait_for_url
def wait_for_url(self,*a,**k):
    r=_wfu(self,*a,**k); _dismiss(self); return r
Page.goto=goto; Page.reload=reload; Page.wait_for_url=wait_for_url
