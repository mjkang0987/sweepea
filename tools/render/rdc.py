# DC 보드 미리보기: sc-for·sc-if(점 경로) 지원. usage: rdc.py out.png file:theme:stateJSON ...
import re,sys,json
from playwright.sync_api import sync_playwright
out=sys.argv[1]; items=sys.argv[2:]
ENGINE=r'''(args)=>{const [vals]=args;
const get=(sc,p)=>p.split('.').reduce((o,k)=>o==null?undefined:o[k],sc);
const sub=(str,sc)=>str.replace(/\{\{([\w.]+)\}\}/g,(_,p)=>{const v=get(sc,p);return typeof v==='function'?'':String(v??'')});
function walk(node,sc){
 for(const ch of [...node.childNodes]){
  if(ch.nodeType===3){ch.textContent=sub(ch.textContent,sc);continue}
  if(ch.nodeType!==1)continue;
  const tag=ch.tagName.toLowerCase();
  if(tag==='sc-if'){const v=get(sc,ch.getAttribute('value').replace(/[{}]/g,''));
    if(v){walk(ch,sc);ch.replaceWith(...ch.childNodes)}else ch.remove();continue}
  if(tag==='sc-for'){const list=get(sc,ch.getAttribute('list').replace(/[{}]/g,''))||[];const as=ch.getAttribute('as');
    const frag=document.createDocumentFragment();
    for(const it of list){const c=ch.cloneNode(true);walk(c,{...sc,[as]:it});frag.append(...c.childNodes)}
    ch.replaceWith(frag);continue}
  for(const a of [...ch.attributes]){if(a.value.includes('{{')){const nv=sub(a.value,sc); if(a.name.startsWith('on')) ch.removeAttribute(a.name); else ch.setAttribute(a.name,nv)}}
  walk(ch,sc)}}
walk(document.body,vals)}'''
shots=[]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":int(__import__("os").environ.get("VW","390")),"height":int(__import__("os").environ.get("VH","844"))})
    for i,it in enumerate(items):
        f,th,*st=it.split(':',2)
        s=open('canvas/project/'+f).read().replace('{{theme}}',th)
        m=re.search(r"renderVals\(\) \{(.*)\}\s*\n\}\s*\n</script>",s,re.S)
        js='(function(){const self={props:%s,state:%s,setState(){}};return (function(){%s}).call(self)})()'%(json.dumps({'theme':th}),st[0] if st else 'null',m.group(1))
        v=pg.evaluate(js)
        h=re.sub(r'<script.*?</script>','',s,flags=re.S).replace('src="/_blob/','data-x="')
        pg.set_content(h); pg.evaluate(ENGINE,[v]); pg.wait_for_timeout(150)
        fn=f'render/_d{i}.png'; pg.screenshot(path=fn); shots.append(fn)
    from PIL import Image
    ims=[Image.open(x) for x in shots]; W=sum(i.width for i in ims)+10*(len(ims)-1)
    o=Image.new('RGB',(W,ims[0].height),'#888'); x=0
    for im in ims: o.paste(im,(x,0)); x+=im.width+10
    o.save(out); b.close()
