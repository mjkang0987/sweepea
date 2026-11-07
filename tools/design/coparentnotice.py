# 함께 관리 시작 알림(사용자 2026-10-29 "아빠 접속했다고 알람은 안 뜨네?"): 상대 엄빠가 초대를 받아 들어오면
# 먼저 있던 엄빠가 다음에 앨범을 열 때 가운데 레이어 한 번. LayerJoin 보드를 바탕으로 글·버튼만 바꿈. 라이트·다크
import os,json,re
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    s=open(f'LayerJoin{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>함께 관리 시작</title>',s,count=1)
    s=re.sub(r'(<h2 id="l1-t"[^>]*>).*?</h2>',r'\1아빠가 앨범을<br>함께 관리하기 시작했어요</h2>',s,count=1,flags=re.S)
    s=re.sub(r'(<p id="l1-d"[^>]*>).*?</p>',r'\1이제 사진 올리기·가족 승인·설정을 같이 할 수 있어요.</p>',s,count=1,flags=re.S)
    s=re.sub(r'(<a href="Family[^"]*"[^>]*>)확인하기</a>',r'\1좋아요</a>',s,count=1)
    s=re.sub(r'\s*<button type="button"[^>]*>나중에</button>','',s,count=1)
    s=s.replace('>✨</span>','>😊</span>',1)
    n=f'LayerCoParentJoined{t}.dc.html'; open(n,'w').write(s)
    ref=B[f'LayerJoin{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
    B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · 부모 · 함께 관리 시작 알림(한 번)')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
