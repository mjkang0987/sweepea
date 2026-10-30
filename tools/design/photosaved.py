# 사진 정보 수정 저장 뒤 그 자리에서 토스트(디자인 146 PhotoSavedToast, -Light): ParentPhoto 보드 그대로 + 탭바 위 12px '저장했어요.'
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
TOAST='''  <p role="status" class="sp-glass-clear" style="position: absolute; left: 20px; right: 20px; bottom: 93px; z-index: 5; margin: 0; display: flex; align-items: center; gap: 12px; min-height: 60px; box-sizing: border-box; padding: 10px 16px; border-radius: 18px;"><span style="flex: 1; font-size: 19px; line-height: 26px; font-weight: 600; word-break: keep-all;">저장했어요.</span></p>
'''
src=open('ToastSent.dc.html').read()
tok=re.search(r'(\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n)',src,re.S).group(1)
glass=re.search(r'\.sp-glass-clear\{.*\n',src).group(0)
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    s=open('ParentPhoto'+t+'.dc.html').read()
    s=re.sub(r'\.sp-t\{.*?\n\.sp-dark\{.*?\n@media \(prefers-color-scheme: dark\)\{.*?\n',lambda m:tok+glass,s,count=1,flags=re.S)
    s=re.sub(r'<title>.*?</title>','<title>사진 정보 수정 · 저장했어요</title>',s,count=1)
    k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k)
    s=s[:k]+TOAST+s[k:]
    name='PhotoSavedToast'+t+'.dc.html'
    open(name,'w').write(s)
    x=b['ParentPhoto'+t+'.dc.html']
    if name not in d['order']: d['order'].append(name)
    b[name]=dict(x,x=5640,title=x['title']+' · 저장했어요 토스트')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
