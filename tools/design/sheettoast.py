# 시트에서 보낸 뒤 토스트(CommentSheetToast, -Light): 시트가 열린 채 입력칸 바로 위에 토스트
import os,re,json
os.chdir('/home/claude/sweepea/tools/canvas/project')
ref=open('/home/claude/sweepea/tools/design/toast_ref.html').read()
heart=re.search(r'(<span aria-hidden="true" class="sp-beat".*?</svg></span>)',ref,re.S).group(1)
spark=re.search(r'(<span aria-hidden="true" class="sp-twinkle".*?</svg></span>)',ref,re.S).group(1)
src=open('ToastSent.dc.html').read()
GL=re.search(r'(\.sp-glass-clear\{.*?\}\}\n)',src,re.S).group(1)
CARD='<div role="status" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: BOTTOMpx; z-index: 100; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;"><span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;">TEXT</span></div>'
B=int(os.environ.get('B','104'))
for name,text,title in [('CommentSheetToast','보냈어요. 가족도 볼 수 있어요.','시트에서 보낸 뒤 토스트'),('CommentSheetDeleted','한마디를 지웠어요.','한마디 지운 뒤 토스트')]:
 for theme in ['','-Light']:
     base=open('CommentSheet'+theme+'.dc.html').read()
     base=base.replace('--panel:rgba(255,255,255,0.75);','--panel:rgba(255,255,255,0.75);--glass-clear:rgba(255,255,255,0.72);--glass-edge:rgba(255,255,255,0.85);').replace('--panel:rgba(0,0,0,0.65);','--panel:rgba(0,0,0,0.65);--glass-clear:rgba(44,44,46,0.6);--glass-edge:rgba(255,255,255,0.22);')
     k=base.index('</style>'); base=base[:k]+GL+base[k:]
     base=re.sub(r'<title>.*?</title>','<title>%s</title>'%title,base,count=1)
     # 지우기 확인은 닫힌 상태로
     base=re.sub(r'<form style="display: flex; align-items: center; gap: 8px; margin-top: 6px;.*?</form>','',base,flags=re.S).replace('<details OPEN','<details')
     k=base.rfind('</main>'); base=base[:k]+CARD.replace('BOTTOM',str(B)).replace('TEXT',text)+'\n'+base[k:]
     open(name+theme+'.dc.html','w').write(base)
d=json.load(open('canvas.json')); b=d['boards']
for i,(n,t) in enumerate([('CommentSheetToast','시트에서 보낸 뒤 토스트'),('CommentSheetDeleted','한마디 지운 뒤 토스트')]):
    b[n+'.dc.html']={'x':6110+i*470,'y':4238,'w':390,'h':844,'title':'다크 · 조부모 웹 · '+t,'is_interactive':True}
    b[n+'-Light.dc.html']={'x':6110+i*470,'y':5172,'w':390,'h':844,'title':'라이트 · 조부모 웹 · '+t,'is_interactive':True}
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
