# 떠 있는 유리 캡슐 탭바(사용자 2026-10-29 "애플 하단 원형 유리 네비게이션", iOS 26 리퀴드 글래스 탭바 느낌):
# 화면 끝에 붙은 막대 대신 양옆·아래 여백을 둔 캡슐, 기존 유리 토큰(sp-glass-clear), 고른 탭은 둥근 강조(--fill). 내용은 탭바 밑으로 흐리게 비침.
# 캡슐 오른쪽에 둥근 유리 '사진 추가(+)' 버튼(사용자 "하단 네비에 사진 추가 버튼 하나", iOS 26 탭바 옆 원형 버튼처럼). 앨범 위 '사진 추가하기'는 뺌.
# 엄빠 홈(ParentHomeGlass)·설정(SettingsGlass) 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
NAV_STYLE='position: absolute; z-index: 6; left: 20px; right: 96px; bottom: 26px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px; padding: 6px; border-radius: 999px;'
def glass(src,dst,title,t):
    s=open(src).read()
    s=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',s,count=1)
    # 유리 스타일이 없는 보드면 홈 보드의 helmet을 씀
    if '.sp-glass-clear{' not in s:
        h=open(f'ParentHome{t}.dc.html').read()
        s=s[:s.index('<helmet>')]+h[h.index('<helmet>'):h.index('</helmet>')]+s[s.index('</helmet>'):]
    a=s.index('<nav aria-label="탭"'); b=s.index('</nav>',a)+len('</nav>')
    nav=s[a:b]
    nav=re.sub(r'<nav aria-label="탭" style="[^"]*">',f'<nav aria-label="탭" class="sp-glass-clear" style="{NAV_STYLE}">',nav)
    # 탭 하나: 캡슐 안 둥근 칸, 고른 탭은 --fill 강조
    nav=re.sub(r'(<a [^>]*?)style="(position: relative; )?display: flex; flex-direction: column; align-items: center; gap: 2px; min-height: 44px;',
               lambda m: m.group(1)+'style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; min-height: 52px; border-radius: 999px;',nav)
    nav=re.sub(r'(<a [^>]*aria-current="page"[^>]*?style=")',r'\1background: var(--fill); ',nav)
    # 배지 자리: 아이콘 오른쪽 위
    nav=nav.replace('top: -2px; left: calc(50% + 6px);','top: 2px; left: calc(50% + 6px);')
    add=(f'<a href="ParentUpload{t}.dc.html" class="sp-glass-tint" aria-label="사진 추가" style="position: absolute; z-index: 6; right: 20px; bottom: 26px; width: 64px; height: 64px; border-radius: 999px; display: flex; align-items: center; justify-content: center; text-decoration: none;">'
         '<svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" style="stroke: var(--on-pea)" stroke-width="2.2" stroke-linecap="round"></path></svg></a>')
    s=s[:a]+nav+'\n  '+add+s[b:]
    # 앨범 위에 떠 있던 '사진 추가하기'는 탭바 옆 버튼으로 옮겨 뺌
    s=re.sub(r'\s*<a href="ParentUpload[^"]*" class="sp-glass-tint" style="position: absolute; left: 50%;.*?</a>','',s,count=1,flags=re.S)
    open(dst,'w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    for base,name,label in [('ParentHome','ParentHomeGlass','부모 · 떠 있는 유리 탭바(앨범)'),('Settings','SettingsGlass','부모 · 떠 있는 유리 탭바(설정)')]:
        n=f'{name}{t}.dc.html'; glass(f'{base}{t}.dc.html',n,'떠 있는 유리 탭바',t)
        ref=B[base+t+'.dc.html']
        if n not in d['order']: d['order'].append(n)
        x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
        B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · '+label)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
