# 설정 > 가족 그 자리에서(디자인 143): 거절 확인 레이어(FamilyRejectLayer), 내 가족 아님 확인 레이어(FamilyRevokeLayer),
# 승인 뒤 토스트(FamilyApprovedToast). Family 보드 위에 PhotoDeleteLayer와 같은 레이어, 토스트는 ToastSent 카드를 탭바 위 12px에
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))

def layer(t,d,ok):
    return f'''  <div class="sp-layer-scrim" aria-hidden="true" style="position: absolute; inset: 0; z-index: 50; background: rgba(0,0,0,0.45);"></div>
  <dialog class="sp-layer-box" open aria-labelledby="fl-t" aria-describedby="fl-d" style="position: absolute; z-index: 51; left: 20px; right: 20px; top: 50%; transform: translateY(-50%); margin: 0; width: auto; box-sizing: border-box; padding: 24px 20px 20px; border: 0; border-radius: 22px; background: var(--surface); color: var(--label); display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; word-break: keep-all;">
    <h2 id="fl-t" style="margin: 0; font-size: 20px; line-height: 26px; font-weight: 700;">{t}</h2>
    <p id="fl-d" style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">{d}</p>
    <div style="align-self: stretch; display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--danger); color: var(--bg); font-family: inherit; font-size: 17px; font-weight: 600;">{ok}</button>
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">취소</button>
    </div>
  </dialog>
'''
TOAST='''  <p role="status" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: 93px; z-index: 5; margin: 0; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;"><span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;">승인했어요. 이제 가족 앨범을 다 볼 수 있어요.</span></p>
'''
# 토큰은 ToastSent 것(위험·유리 색 포함)으로
tok=re.search(r'(\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n)',open('ToastSent.dc.html').read(),re.S).group(1)
glass=re.search(r'\.sp-glass-clear\{.*\n',open('ToastSent.dc.html').read()).group(0)
boards={
 'FamilyRejectLayer':('거절 확인',lambda s:s+layer('큰이모 거절할까요?','그 휴대폰은 다시 들어올 수 없어요. 되돌릴 수 없어요.','거절')),
 'FamilyRevokeLayer':('내 가족 아님 확인',lambda s:s+layer('외할머니 휴대폰을 내 가족 아님으로 할까요?','그 휴대폰은 다시 들어올 수 없어요. 되돌릴 수 없어요.','내 가족 아님')),
 'FamilyApprovedToast':('승인 뒤 토스트',None),
}
d=json.load(open('canvas.json')); b=d['boards']
for i,(name,(title,add)) in enumerate(boards.items()):
    for t in ['','-Light']:
        s=open('Family'+t+'.dc.html').read()
        s=re.sub(r'\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n',lambda m:tok+glass,s,count=1,flags=re.S)
        s=re.sub(r'<title>.*?</title>',f'<title>설정 · 가족 · {title}</title>',s,count=1)
        k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k)
        if add: s=s[:k]+add('')+s[k:]
        else:
            # 승인한 사람 카드가 그 자리에서 빠짐(새 기기가 남아 설정 탭 배지는 1)
            s=re.sub(r'<span id="f-wait">승인 기다리는 사람</span> · 1</h2>\s*<article.*?</article>','<span id="f-wait">승인 기다리는 사람</span> · 0</h2>\n      <p style="margin: 0 0 0 16px; font-size: 15px; line-height: 21px; color: var(--label-2);">지금은 없어요.</p>',s,count=1,flags=re.S)
            k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k)
            s=s[:k]+TOAST+s[k:]
        open(name+t+'.dc.html','w').write(s)
        src=b['Family'+t+'.dc.html']
        if name+t+'.dc.html' not in d['order']: d['order'].append(name+t+'.dc.html')
        b[name+t+'.dc.html']=dict(src,x=3760+470*i,title=src['title'].replace(' (승인)','')+' · '+title)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
