# 저장 버튼 아래 고정(디자인 151, 사용자 2026-10-27 "저장하기 같은 하단 버튼 하단 fixed"): 입력 화면의 맨 아래 주요 버튼을 탭바 바로 위 막대로.
# 접종·검진은 디자인대로 체크하면 바로 저장 + 토스트(HealthSavedToast)
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
BAR='<div style="position: absolute; left: 0; right: 0; bottom: 81px; z-index: 4; box-sizing: border-box; padding: 12px 20px; background: var(--bar); border-top: 1px solid var(--separator); -webkit-backdrop-filter: blur(20px); backdrop-filter: blur(20px);">{btn}</div>\n'
BTN=re.compile(r'<button type="button" style="(min-height: 52px; border: 0; border-radius: 1[24]px;[^"]*background: var\(--pea\);[^"]*)">(저장|추가)</button>')
def bar(s):
    m=BTN.search(s); assert m, 'no button'
    btn=f'<button type="button" style="width: 100%; {m.group(1)}">{m.group(2)}</button>'
    # 버튼만 있던 감싸개는 같이 뺀다
    w=re.search(r'\s*<div style="margin-top: auto; padding-bottom: 16px; display: flex; flex-direction: column;">'+re.escape(m.group(0))+r'</div>',s)
    s=s.replace(w.group(0),'') if w else s.replace(m.group(0),'',1)
    k=s.index('<nav aria-label="탭"')
    return s[:k]+BAR.format(btn=btn)+'  '+s[k:]
changed=[]
for base in ['ChildAdd','PasswordChange','ParentPhoto','PhotoSavedToast','PhotoDeleteLayer']:
    for t in ['','-Light']:
        f=base+t+'.dc.html'; s=open(f).read()
        if 'bottom: 81px; z-index: 4' in s: continue
        s=bar(s)
        if base=='PhotoSavedToast': s=s.replace('bottom: 93px; z-index: 5','bottom: 170px; z-index: 5')
        open(f,'w').write(s); changed.append(f)
# 접종: 바로 저장 토스트
src=open('ToastSent.dc.html').read()
tok=re.search(r'(\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n)',src,re.S).group(1)
glass=re.search(r'\.sp-glass-clear\{.*\n',src).group(0)
T='''  <p role="status" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: 93px; z-index: 5; margin: 0; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;"><span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;">저장했어요.</span></p>
'''
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    s=open('Health'+t+'.dc.html').read()
    s=re.sub(r'\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n',lambda m:tok+glass,s,count=1,flags=re.S)
    s=re.sub(r'<title>(.*?)</title>',lambda m:f'<title>{m.group(1)} · 저장 토스트</title>',s,count=1)
    k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k); s=s[:k]+T+s[k:]
    n='HealthSavedToast'+t+'.dc.html'; open(n,'w').write(s); changed.append(n)
    sb=b['Health'+t+'.dc.html']
    if n not in b:
        x=max(v['x'] for v in b.values() if v['y']==sb['y'])+470
        d['order'].append(n); b[n]=dict(sb,x=x,title=sb['title']+' · 저장 토스트')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print(' '.join(changed))
