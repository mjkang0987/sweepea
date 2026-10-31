# 엄빠 앨범 넘겨 보기·모아 보기(98d, 사용자 2026-10-29 "모아보기 넘겨보기도 없고"): ParentHomeZoom3에서
# 머리 아래 세그먼트 '넘겨 보기 · 모아 보기' + 가족 넘겨 보기(GrandHome)와 같은 카드. 반응 줄은 없음(크게 보기에서), −/+도 없음(모아 보기 것)
# 모아 보기 보드(ParentHomeZoom*)에도 같은 세그먼트를 넣는다. 다시 돌려도 같게
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
def seg(swipe,t):
    on='background: var(--seg); box-shadow: 0 1px 2px rgba(0,0,0,0.12); font-weight: 600;'
    item='flex: 1 0 auto; padding: 0 20px; white-space: nowrap; min-height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 8px; text-decoration: none; color: var(--label); font-size: 15px; '
    a=lambda href,label,cur: f'<a href="{href}"{" aria-current=\"page\"" if cur else ""} style="{item}{on if cur else "font-weight: 500;"}">{label}</a>'
    return ('<nav aria-label="보기 방식" data-view-seg style="margin: 0 20px; display: flex; gap: 2px; padding: 2px; background: var(--fill); border-radius: 10px;">'
            +a(f'ParentHomeSwipe{t}.dc.html','넘겨 보기',swipe)+a(f'ParentHomeZoom3{t}.dc.html','모아 보기',not swipe)+'</nav>\n    ')
def add_seg(s,swipe,t):
    s=re.sub(r'<nav aria-label="보기 방식" data-view-seg.*?</nav>\n    ','',s,flags=re.S)
    return s.replace('<fieldset',seg(swipe,t)+'<fieldset',1)
def card(left,ph,side,t):
    # 양옆 카드: 안쪽 모서리를 축으로 기울이고 반투명(가족 GrandHome과 같은 값)
    tf={'prev':'transform: perspective(900px) rotateY(18deg) scale(0.86); transform-origin: right center; opacity: 0.5; z-index: 1;',
        'next':'transform: perspective(900px) rotateY(-18deg) scale(0.86); transform-origin: left center; opacity: 0.5; z-index: 1;'}[side]
    return (f'<a href="ParentView{t}.dc.html" aria-label="{"이전" if side=="prev" else "다음"} 사진" style="position: absolute; top: 18px; left: {left}px; width: 290px; height: 328px; border-radius: 20px; overflow: hidden; background: var(--surface); {tf}">'
            f'<span style="display: block; height: 268px; background: var(--ph-{ph});"></span></a>')
def swipe(t):
    s=open(f'ParentHomeZoom3{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>앨범 넘겨 보기</title>',s,count=1)
    s=s.replace('>10월 1일 ~ 21일</p>','>사진 1,284 · 영상 37</p>',1)
    # −/+는 모아 보기 것
    s=re.sub(r'\s*<nav aria-label="사진 크기".*?</nav>','',s,count=1,flags=re.S)
    s=add_seg(s,True,t)
    i=s.index('<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px;')
    j=s.index('</div></div>',i)+len('</div></div>')
    heart=('<span aria-hidden="true" style="display: flex; gap: 10px; color: var(--label); font-weight: 600;">'
           '<span style="display: flex; align-items: center; gap: 3px;"><span style="color: var(--blossom);">♥</span>3</span>'
           '<span style="display: flex; align-items: center; gap: 3px;"><svg width="14" height="14" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z" fill="none" style="stroke: var(--label)" stroke-width="2" stroke-linejoin="round"></path></svg>1</span></span>')
    carousel=('<section aria-label="사진 1,321장, 옆으로 밀어서 넘겨 보기" style="display: flex; flex-direction: column; gap: 12px;">'
              '<div style="position: relative; height: 360px; overflow-x: clip;">'
              +card(-226,2,'prev',t)+card(326,2,'next',t)+
              f'<a href="ParentView{t}.dc.html" aria-label="10월 21일 · 하린 100일 사진, 하트 3개, 한마디 1개 크게 보기" style="position: absolute; top: 0; left: 50px; width: 290px; height: 360px; border-radius: 20px; overflow: hidden; background: var(--surface); z-index: 2; box-shadow: 0 8px 20px rgba(0,0,0,0.16), 0 2px 6px rgba(0,0,0,0.08); display: flex; flex-direction: column; color: var(--label-2); text-decoration: none;">'
              '<span style="flex: 1; background: var(--ph-1);"></span>'
              '<span style="flex: none; min-height: 44px; display: flex; align-items: center; gap: 8px; padding: 4px 16px; box-sizing: border-box; font-size: 15px; line-height: 20px; font-weight: 500;">'
              f'<span style="flex: 1;">10월 21일 · 하린 100일</span>{heart}</span></a>'
              '</div>'
              '<p style="margin: 0; text-align: center; font-size: 15px; line-height: 20px; font-weight: 500; color: var(--label-2);"><strong style="color: var(--label); font-weight: 700;">1</strong> / 1,321 · 옆으로 밀거나 옆 사진을 누르세요</p>'
              '</section>')
    s=s[:i]+carousel+s[j:]
    open(f'ParentHomeSwipe{t}.dc.html','w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    swipe(t)
    for z in [1,3,5,'m','y']:
        n=f'ParentHomeZoom{z}{t}.dc.html'
        s=open(n).read(); open(n,'w').write(add_seg(s,False,t))
    ref=B[f'ParentHomeZoom3{t}.dc.html']; n=f'ParentHomeSwipe{t}.dc.html'
    if n not in d['order']: d['order'].append(n)
    x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
    B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · 부모 · 넘겨 보기(카드 옆으로 밀기, 누르면 크게 보기)')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
