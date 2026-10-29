# 엄빠 앨범 사진 크기 −/+ (98a, 사용자 2026-10-29 "엄빠 화면에도 + - 있어야지"): ParentHomeBleed 머리 오른쪽에 둥근 유리 −/+ (사진 앱 보관함 버튼 자리).
# 칸 단계는 가족과 같은 1·2·3칸(사진 전부) → 월별(달 카드: 대표 3장 + 'N장', 사용자 "줄여 보는 건 대표 사진 몇 장"). 보드: 3칸·1칸·월별
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
def btn(label,sign,off=False):
    o=' opacity: 0.35;' if off else ''
    return (f'<a href="#" aria-label="{label}" class="sp-glass-clear" style="width: 44px; height: 44px; border-radius: 999px; display: flex; align-items: center; justify-content: center; text-decoration: none; color: var(--label); font-size: 24px; line-height: 1;{o}">{sign}</a>')
def zoom(t,z):
    s=open(f'ParentHomeBleed{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>앨범 사진 크기</title>',s,count=1)
    nav=('<nav aria-label="사진 크기" style="position: absolute; top: 54px; right: 20px; display: flex; gap: 8px;">'
         +btn('작게(한 줄에 더 많이)','−',z=='m')+btn('크게(한 줄에 더 적게)','+',z==1)+'</nav>')
    s=s.replace('</header>',nav+'</header>',1)
    i=s.index('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2px;')
    depth=0
    for m in re.finditer(r'<(/?)div\b',s[i:]):
        depth+= -1 if m.group(1) else 1
        if depth==0: j=i+s[i+m.start():].index('>')+m.start()+1; break
    if z==3:
        cells=''.join(f'<div role="img" aria-label="사진" style="aspect-ratio: 1; background: var(--ph-{1+k%2});"></div>' for k in range(15))
        grid=f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px;">{cells}</div>'
    elif z=='m':
        def card(title,n,k):
            pics=''.join(f'<span style="aspect-ratio: 1; background: var(--ph-{1+(k+i)%2});"></span>' for i in range(3))
            return (f'<a href="#" style="display: grid; grid-template-columns: minmax(0, 1fr) auto; row-gap: 8px; align-items: baseline; color: var(--label); text-decoration: none;">'
                    f'<span style="grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px; border-radius: 12px; overflow: hidden;">{pics}</span>'
                    f'<span style="font-size: 22px; line-height: 28px; font-weight: 700;">{title}</span><span style="font-size: 13px; color: var(--label-2);">{n}장</span></a>')
        grid=f'<div style="display: grid; gap: 20px; padding: 0 20px;">{card("10월",48,0)}{card("9월",112,1)}{card("8월",86,0)}</div>'
    else:
        grid=('<div style="display: flex; flex-direction: column; gap: 2px;">'
              '<div role="img" aria-label="사진, 하트 3개 한마디 1개" style="position: relative; aspect-ratio: 3 / 4; background: var(--ph-1);"></div>'
              '<div role="img" aria-label="사진" style="aspect-ratio: 4 / 3; background: var(--ph-2);"></div></div>')
    s=s[:i]+grid+s[j:]
    # 월별은 달 카드에 달 이름이 있어 위 달 제목 줄은 뺌
    if z=='m': s=re.sub(r'<div style="margin-inline: 20px; display: flex; align-items: baseline; justify-content: space-between;.*?</div>','',s,count=1,flags=re.S)
    open(f'ParentHomeZoom{z}{t}.dc.html','w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    ref=B[f'ParentHomeBleed{t}.dc.html']
    for z,label in [(3,'3칸(정사각, 사진 전부)'),(1,'1칸(한 장씩 원래 모양)'),('m','월별(달 카드, 대표 3장)')]:
        zoom(t,z); n=f'ParentHomeZoom{z}{t}.dc.html'
        if n not in d['order']: d['order'].append(n)
        x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
        B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+f' · 부모 · 사진 크기 −/+ {label}')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
