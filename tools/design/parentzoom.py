# 엄빠 앨범 사진 크기 −/+ (98a, 사용자 2026-10-29 "엄빠 화면에도 + - 있어야지"): ParentHomeBleed 머리 오른쪽에 둥근 유리 −/+ (사진 앱 보관함 버튼 자리).
# 칸 단계는 가족과 같은 1·2·3·5칸(사진 전부) → 월별 → 연별(98c, 시안 GrandList 카드 배치, 날짜는 사진 위). 머리 작은 줄은 화면 맨 위 사진의 찍은 날(3·5칸은 기간)
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
def btn(label,sign,off=False):
    o=' opacity: 0.35;' if off else ''
    return (f'<a href="#" aria-label="{label}" style="width: 44px; height: 44px; border-radius: 999px; display: flex; align-items: center; justify-content: center; text-decoration: none; color: var(--label); font-size: 24px; line-height: 1;{o}">{sign}</a>')
def zoom(t,z):
    s=open(f'ParentHomeBleed{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>앨범 사진 크기</title>',s,count=1)
    # 오른쪽 아래 떠 있는 유리 알약(사용자 "플러스 마이너스 버튼 아래에, 우측 아래 플로팅"), 탭바 위
    nav=('<nav aria-label="사진 크기" class="sp-glass-clear" style="position: absolute; z-index: 6; right: 20px; bottom: 102px; display: flex; padding: 2px; border-radius: 999px;">'
         +btn('작게(한 줄에 더 많이)','−',z=='y')+btn('크게(한 줄에 더 적게)','+',z==1)+'</nav>')
    when={1:'10월 21일 · 생후 13개월',3:'10월 1일 ~ 21일',5:'9월 3일 ~ 10월 21일'}.get(z)
    if when: s=s.replace('>사진 1,284 · 영상 37</p>','>'+when+'</p>',1)
    s=s.replace('</main>','</main>\n  '+nav,1)
    i=s.index('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2px;')
    depth=0
    for m in re.finditer(r'<(/?)div\b',s[i:]):
        depth+= -1 if m.group(1) else 1
        if depth==0: j=i+s[i+m.start():].index('>')+m.start()+1; break
    if z==3:
        cells=''.join(f'<div role="img" aria-label="사진" style="aspect-ratio: 1; background: var(--ph-{1+k%2});"></div>' for k in range(15))
        grid=f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px;">{cells}</div>'
    elif z==5:
        cells=''.join(f'<div role="img" aria-label="사진" style="aspect-ratio: 1; background: var(--ph-{1+k%2});"></div>' for k in range(30))
        grid=f'<div style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 2px;">{cells}</div>'
    elif z in ('m','y'):
        # 시안 GrandList: 월별 = 왼쪽 큰 1장(두 줄) + 오른쪽 2장, 연별 = 왼쪽 큰 1장(2×2) + 오른쪽 작은 4장. 날짜·장 수는 사진 위(사용자 "날짜가 사진 위에")
        def card(title,sub,k):
            if z=='m':
                pics=(f'<span style="grid-row: span 2; background: var(--ph-{1+k%2});"></span>'
                      f'<span style="grid-column: span 2; background: var(--ph-{2-k%2});"></span><span style="grid-column: span 2; background: var(--ph-{1+k%2});"></span>')
                grid_css='grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: repeat(2, minmax(0, 1fr)); height: 180px;'
            else:
                pics=(f'<span style="grid-column: span 2; grid-row: span 2; background: var(--ph-{1+k%2});"></span>'
                      +''.join(f'<span style="background: var(--ph-{1+(k+i)%2});"></span>' for i in range(1,5)))
                grid_css='grid-template-columns: repeat(4, minmax(0, 1fr)); grid-template-rows: repeat(2, minmax(0, 1fr)); height: 220px;'
            return (f'<a href="#" style="position: relative; display: block; border-radius: 20px; overflow: hidden; color: #fff; text-decoration: none;">'
                    f'<span style="display: grid; {grid_css} gap: 2px;">{pics}</span>'
                    '<span style="position: absolute; left: 0; right: 0; bottom: 0; display: flex; flex-direction: column; padding: 40px 16px 14px; background: linear-gradient(transparent, rgba(0,0,0,0.6));">'
                    f'<strong style="font-size: 22px; line-height: 28px; font-weight: 700;">{title}</strong><span style="font-size: 15px; line-height: 20px;">{sub}</span></span></a>')
        items=[("10월","26장"),("9월","112장"),("8월","86장")] if z=='m' else [("2026년","1–10월 · 312장"),("2025년","9–12월 · 148장")]
        grid='<div style="display: grid; gap: 16px; padding: 0 20px;">'+''.join(card(t,sb,k) for k,(t,sb) in enumerate(items))+'</div>'
    else:
        grid=('<div style="display: flex; flex-direction: column; gap: 2px;">'
              '<div role="img" aria-label="사진, 하트 3개 한마디 1개" style="position: relative; aspect-ratio: 3 / 4; background: var(--ph-1);"></div>'
              '<div role="img" aria-label="사진" style="aspect-ratio: 4 / 3; background: var(--ph-2);"></div></div>')
    s=s[:i]+grid+s[j:]
    # 월별은 달 카드에 달 이름이 있어 위 달 제목 줄은 뺌
    # 달 제목 줄은 위 날짜 줄과 겹쳐 뺌(사용자 "중복 내용", 생후 개월은 날짜 줄로)
    if True: s=re.sub(r'<div style="margin-inline: 20px; display: flex; align-items: baseline; justify-content: space-between;.*?</div>','',s,count=1,flags=re.S)
    open(f'ParentHomeZoom{z}{t}.dc.html','w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    ref=B[f'ParentHomeBleed{t}.dc.html']
    for z,label in [(3,'3칸(정사각, 기간 표시)'),(1,'1칸(한 장씩, 찍은 날 표시)'),(5,'5칸(정사각, 기간 표시)'),('m','월별(왼쪽 큰 1장 + 2장, 날짜는 사진 위)'),('y','연별(왼쪽 큰 1장 + 4장)')]:
        zoom(t,z); n=f'ParentHomeZoom{z}{t}.dc.html'
        if n not in d['order']: d['order'].append(n)
        x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
        B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+f' · 부모 · 사진 크기 −/+ {label}')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
