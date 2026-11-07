# 보드 움직임을 정해진 시각(ms)마다 찍어 한 장으로. 사용: frames.py out.png T_board.dc.html theme ms,ms,...
import re,sys,json,os
sys.path.insert(0,os.path.dirname(__file__))
from playwright.sync_api import sync_playwright
from PIL import Image
out,f,th,times=sys.argv[1],sys.argv[2],sys.argv[3],[int(x) for x in sys.argv[4].split(',')]
src=open('render/rdc.py').read(); ENGINE=re.search(r"ENGINE=r'''(.*?)'''",src,re.S).group(1)
s=open('canvas/project/'+f).read().replace('{{theme}}',th)
m=re.search(r"renderVals\(\) \{(.*)\}\s*\n\}\s*\n</script>",s,re.S)
h=re.sub(r'<script.*?</script>','',s,flags=re.S)
ims=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844})
    js='(function(){const self={props:%s,state:null,setState(){}};return (function(){%s}).call(self)})()'%(json.dumps({'theme':th}),m.group(1))
    v=pg.evaluate(js)
    # 움직임을 멈춘 채 그려 놓고, 시각마다 애니메이션 위치를 직접 정해 찍는다
    pg.set_content(h); pg.evaluate(ENGINE,[v])
    for t in times:
        pg.evaluate('t=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=t})',t)
        fn='render/_f%d.png'%t; pg.screenshot(path=fn); ims.append(Image.open(fn))
    b.close()
W=sum(i.width for i in ims)+10*(len(ims)-1); o=Image.new('RGB',(W,ims[0].height),'#888'); x=0
for im in ims: o.paste(im,(x,0)); x+=im.width+10
o.save(out)
