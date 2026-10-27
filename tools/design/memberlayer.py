# 가족 한 명 그 자리에서(디자인 147): 내보내기 확인 레이어(MemberRemoveLayer), 올리기 허용 켠 뒤 토스트(MemberUploadToast). familylayer.py와 같은 방식
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
TEXT='이 사람의 휴대폰은 더 이상 들어올 수 없고, 남긴 반응과 한마디는 가족 화면에서 빠져요. 반응·한마디 기록이 남아 있으면 같은 이름은 다시 쓸 수 없어요. 그룹 비밀번호를 아는 사람이면 다른 이름으로 다시 요청할 수 있지만 승인해야 들어와요.'
def layer(t,d,ok):
    return f'''  <div class="sp-layer-scrim" aria-hidden="true" style="position: absolute; inset: 0; z-index: 50; background: rgba(0,0,0,0.45);"></div>
  <dialog class="sp-layer-box" open aria-labelledby="ml-t" aria-describedby="ml-d" style="position: absolute; z-index: 51; left: 20px; right: 20px; top: 50%; transform: translateY(-50%); margin: 0; width: auto; box-sizing: border-box; padding: 24px 20px 20px; border: 0; border-radius: 22px; background: var(--surface); color: var(--label); display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; word-break: keep-all;">
    <h2 id="ml-t" style="margin: 0; font-size: 20px; line-height: 26px; font-weight: 700;">{t}</h2>
    <p id="ml-d" style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">{d}</p>
    <div style="align-self: stretch; display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--danger); color: var(--bg); font-family: inherit; font-size: 17px; font-weight: 600;">{ok}</button>
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">취소</button>
    </div>
  </dialog>
'''
TOAST='''  <p role="status" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: 93px; z-index: 5; margin: 0; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;"><span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;">이제 사진을 올릴 수 있어요.</span></p>
'''
src=open('ToastSent.dc.html').read()
tok=re.search(r'(\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n)',src,re.S).group(1)
glass=re.search(r'\.sp-glass-clear\{.*\n',src).group(0)
boards={'MemberRemoveLayer':('내보내기 확인',layer('하린 아빠 내보낼까요?',TEXT,'내보내기')),'MemberUploadToast':('올리기 허용 토스트',TOAST)}
d=json.load(open('canvas.json')); b=d['boards']
for i,(name,(title,add)) in enumerate(boards.items()):
    for t in ['','-Light']:
        s=open('MemberDetail'+t+'.dc.html').read()
        s=re.sub(r'\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n',lambda m:tok+glass,s,count=1,flags=re.S)
        s=re.sub(r'<title>.*?</title>',f'<title>하린 아빠 · {title}</title>',s,count=1)
        k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k)
        s=s[:k]+add+s[k:]
        n=name+t+'.dc.html'; open(n,'w').write(s)
        src_b=b['MemberDetail'+t+'.dc.html']
        if n not in d['order']: d['order'].append(n)
        b[n]=dict(src_b,x=5170+470*i,title=src_b['title']+' · '+title)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
