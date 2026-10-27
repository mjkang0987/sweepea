# 사진만 보기(대기열 C, 디자인 157): 크게 보기에서 사진을 한 번 누르면 위 메뉴·아래 판·화살표·영상 막대가 사라지고 검은 바탕에 사진만, 다시 누르면 돌아옴.
# 보드 PhotoView에 이미 있는 누르기 전환(uiVisible)을 '숨긴 상태'로 시작하는 보드로 따로 둔다
import os,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    src='PhotoView'+t+'.dc.html'; n='PhotoViewBare'+t+'.dc.html'
    s=open(src).read()
    assert '"uiVisible":{"editor":"boolean","default":true}' in s
    open(n,'w').write(s.replace('"uiVisible":{"editor":"boolean","default":true}','"uiVisible":{"editor":"boolean","default":false}'))
    if n not in b:
        r=b[src]; x=max(v['x'] for v in b.values() if v['y']==r['y'])+470
        d['order'].append(n); b[n]=dict(r,x=x,title=('다크' if not t else '라이트')+' · 가족 · 크게 보기 · 사진만(한 번 누름)')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
