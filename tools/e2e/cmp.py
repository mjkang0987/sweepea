from playwright.sync_api import sync_playwright
from PIL import Image
B='http://localhost:4321'; O='/home/claude/sweepea/tools/e2e/'
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={'width':390,'height':844}); pg=c.new_page(); pg.goto(B+'/i/Harin001')
    pg.get_by_role('button',name='외할아버지',exact=True).click(); pg.wait_for_url('**/password**'); pg.fill('#pw','1234'); pg.get_by_role('button',name='들어가기').click(); pg.wait_for_url('**/album')
    pg.wait_for_timeout(400); pg.screenshot(path=O+'c1.png')
    pg.evaluate("document.querySelector('.sp-a__swipe').scrollBy({left:150})"); pg.wait_for_timeout(400); pg.screenshot(path=O+'c2.png')
    d=b.new_context(viewport={'width':390,'height':844},color_scheme='dark'); d.add_cookies(c.cookies()); dp=d.new_page(); dp.goto(B+'/album'); dp.wait_for_timeout(400); dp.screenshot(path=O+'c3.png')
    b.close()
ims=[Image.open('/home/claude/sweepea/tools/render/_d0.png')] if False else []
ims=[Image.open(O+n) for n in ('c1.png','c2.png','c3.png')]
o=Image.new('RGB',(sum(i.width for i in ims)+20,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(O+'cmp.png')
