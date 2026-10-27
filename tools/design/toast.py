# 크게 보기 토스트 보드(아이콘 없음, 사용자 2026-10-27)(ToastSent·ToastError, 라이트·다크): PhotoView 위에 디자인(GrandHome) 토스트 카드
import os,re,json
os.chdir('/home/claude/sweepea/tools/canvas/project')
ref=open('/home/claude/sweepea/tools/design/toast_ref.html').read()
heart=re.search(r'(<span aria-hidden="true" class="sp-beat".*?</svg></span>)',ref,re.S).group(1)
spark=re.search(r'(<span aria-hidden="true" class="sp-twinkle".*?</svg></span>)',ref,re.S).group(1)
GL=".sp-glass-clear{-webkit-backdrop-filter:blur(20px) saturate(180%);backdrop-filter:blur(20px) saturate(180%);background:var(--glass-clear);color:var(--label);box-shadow:inset 0 1px 0 var(--glass-edge),0 0 0 0.5px var(--separator),0 10px 28px rgba(0,0,0,0.16)}@media (prefers-reduced-transparency: reduce){.sp-glass-clear{background:var(--fill);-webkit-backdrop-filter:none;backdrop-filter:none}}"
CARD='<div role="ROLE" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: BOTTOMpx; z-index: 5; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;">ICON<span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;TEXTCOLOR">TEXT</span>TAIL</div>'
ERR='<span aria-hidden="true" style="flex: none; width: 32px; height: 32px; border-radius: 50%; background: var(--danger); color: var(--bg); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; line-height: 1;">!</span>'
for src,theme in [('PhotoView-Light','Light'),('PhotoView','')]:
    base=open(src+'.dc.html').read()
    base=base.replace('--panel:rgba(255,255,255,0.75);}','--panel:rgba(255,255,255,0.75);--danger:#d70015;--glass-clear:rgba(255,255,255,0.72);--glass-edge:rgba(255,255,255,0.85);}').replace('--panel:rgba(0,0,0,0.65);}','--panel:rgba(0,0,0,0.65);--danger:#ff6961;--glass-clear:rgba(44,44,46,0.6);--glass-edge:rgba(255,255,255,0.22);}')
    k=base.index('</style>'); base=base[:k]+GL+'\n'+base[k:]
    for name,card in [('ToastSent',CARD.replace('ROLE','status').replace('ICON','').replace('TEXTCOLOR','').replace('TEXT','보냈어요. 가족 모두 볼 수 있어요.').replace('TAIL','')),
                      ('ToastError',CARD.replace('ROLE','alert').replace('ICON','').replace('TEXTCOLOR','').replace('TEXT','한마디를 써 주세요.').replace('TAIL',''))]:
        s=base.replace('<title>사진 크게 보기</title>','<title>%s</title>'%('한마디 보냄 토스트' if name=='ToastSent' else '한마디 오류 토스트'),1)
        k=s.rfind('</main>'); s=s[:k]+card.replace('BOTTOM','300')+'\n'+s[k:]
        open(name+('-Light' if theme else '')+'.dc.html','w').write(s)
d=json.load(open('canvas.json')); b=d['boards']
for i,(n,t) in enumerate([('ToastSent','한마디 보냄 토스트'),('ToastError','한마디 오류 토스트')]):
    b[n+'.dc.html']={'x':5170+i*470,'y':4238,'w':390,'h':844,'title':'다크 · 조부모 웹 · '+t,'is_interactive':True}
    b[n+'-Light.dc.html']={'x':5170+i*470,'y':5172,'w':390,'h':844,'title':'라이트 · 조부모 웹 · '+t,'is_interactive':True}
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
