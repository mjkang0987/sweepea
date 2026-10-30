# 바로 저장되는 설정 화면들 그 자리에서(디자인 149): 원래 보드 그대로 + 탭바 위 12px 토스트(ToastSent 카드). 보드는 같은 줄 맨 오른쪽 옆에
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
LIST=[('Settings','SettingsDownloadToast','이제 가족 화면에 저장 버튼이 보여요.'),
      ('TextSize','TextSizeSavedToast','저장했어요. 다음에 처음 들어오는 가족부터 적용돼요.'),
      ('ChildSettings','ChildHealthToast','저장했어요.'),
      ('GroupDetail','GroupSavedToast','저장했어요.')]
def toast(text): return f'''  <p role="status" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: 93px; z-index: 5; margin: 0; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;"><span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;">{text}</span></p>
'''
src=open('ToastSent.dc.html').read()
tok=re.search(r'(\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n)',src,re.S).group(1)
glass=re.search(r'\.sp-glass-clear\{.*\n',src).group(0)
d=json.load(open('canvas.json')); b=d['boards']
for base,name,text in LIST:
    for t in ['','-Light']:
        s=open(base+t+'.dc.html').read()
        s=re.sub(r'\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n',lambda m:tok+glass,s,count=1,flags=re.S)
        s=re.sub(r'<title>(.*?)</title>',lambda m:f'<title>{m.group(1)} · 저장 토스트</title>',s,count=1)
        k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k)
        s=s[:k]+toast(text)+s[k:]
        n=name+t+'.dc.html'; open(n,'w').write(s)
        sb=b[base+t+'.dc.html']
        if n not in b:
            x=max(v['x'] for k2,v in b.items() if v['y']==sb['y'])+470
            d['order'].append(n); b[n]=dict(sb,x=x,title=sb['title']+' · 저장 토스트')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
