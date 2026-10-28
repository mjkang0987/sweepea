# 할머니가 보신 기록(95, 경쟁력 기능 1, 사용자 2026-10-29 '이름만'): 엄마아빠 크게 보기 날짜 줄 아래 눈 그림 + "외할머니·외할아버지가 봤어요"
# 횟수·시간·주간 요약은 뺌(감시처럼 읽혀서). 카톡의 1이 사라지는 것과 같은 역할
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
EYE='<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style="flex: none;"><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"></path><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"></circle></svg>'
VIEWERS=f'<p style="margin: -4px 0 0; display: flex; align-items: center; gap: 6px; font-size: 15px; line-height: 21px; color: var(--label-2);">{EYE}<span><strong style="color: var(--label); font-weight: 600;">외할머니·외할아버지</strong>가 봤어요</span></p>'
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    n=f'ParentReactionsViews{t}.dc.html'
    if os.path.exists(n): os.remove(n)
    b.pop(n,None)
    if n in d['order']: d['order'].remove(n)
for t in ['','-Light']:
    # 크게 보기
    s=open(f'ParentView{t}.dc.html').read()
    cap='<div style="display: flex; align-items: center; justify-content: space-between;"><span style="font-size: 17px; line-height: 24px; font-weight: 500; color: var(--label-2);">생후 13개월 · 10월 21일</span></div>'
    assert cap in s
    s=s.replace(cap,cap+VIEWERS,1)
    s=re.sub(r'<title>.*?</title>','<title>사진 크게 보기 · 본 사람</title>',s,count=1)
    n=f'ParentViewViewers{t}.dc.html'; open(n,'w').write(s)
    ref=b[f'ParentView{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    b[n]=dict(ref,x=(max(v['x'] for v in b.values() if v['y']==ref['y'])+470) if n not in b else b[n]['x'],title=ref['title']+' · 본 사람')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
