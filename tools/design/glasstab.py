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
    # 유리 위라 고르지 않은 탭도 진한 글자·아이콘(뒤 사진에 따라 흐린 글자는 대비 부족, 리뷰 2026-10-29)
    nav=nav.replace('color: var(--label-2); text-decoration: none; font-size: 11px','color: var(--label); text-decoration: none; font-size: 11px').replace('style="stroke: var(--label-2)"','style="stroke: var(--label)"')
    # 배지 자리: 아이콘 오른쪽 위
    nav=nav.replace('top: -2px; left: calc(50% + 6px);','top: 2px; left: calc(50% + 6px);')
    add=(f'<a href="ParentUpload{t}.dc.html" class="sp-glass-tint" aria-label="사진 추가" style="position: absolute; z-index: 6; right: 20px; bottom: 26px; width: 64px; height: 64px; border-radius: 999px; display: flex; align-items: center; justify-content: center; text-decoration: none;">'
         '<svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" style="stroke: var(--on-pea)" stroke-width="2.2" stroke-linecap="round"></path></svg></a>')
    s=s[:a]+nav+'\n  '+add+s[b:]
    # 앨범 위에 떠 있던 '사진 추가하기'는 탭바 옆 버튼으로 옮겨 뺌
    s=re.sub(r'\s*<a href="ParentUpload[^"]*" class="sp-glass-tint" style="position: absolute; left: 50%;.*?</a>','',s,count=1,flags=re.S)
    # 아이 카드(콩이·생후·다음 접종)는 홈에서 뺌(사용자 "상단 접종 정보 너무 공간 차지" → 알림 탭 '다가오는 일정'·설정 › 아이로 이관)
    s=re.sub(r'\s*<a href="Health[^"]*" style="display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 16px;.*?</a>','',s,count=1,flags=re.S)
    open(dst,'w').write(s)
SYR=('<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" style="flex: none;"><path d="M14 4l6 6M17 7l-9 9-3 1 1-3 9-9M11 7l6 6M8 13l1.5 1.5M10 11l1.5 1.5M4 20l2-2" fill="none" style="stroke: var(--pea-ink)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path></svg>')
def reactions(t):
    glass(f'ParentReactions{t}.dc.html',f'ReactionsHealth{t}.dc.html','알림 · 다가오는 일정',t)
    n=f'ReactionsHealth{t}.dc.html'; s=open(n).read()
    anchor='앱이 나오면 알림으로도 알려 드릴게요.</p>'
    card=('\n    <section aria-labelledby="r-soon"><h2 id="r-soon" style="margin: 0 0 8px 16px; font-size: 13px; line-height: 18px; font-weight: 600; color: var(--label-2);">다가오는 일정</h2>'
          f'<a href="Health{t}.dc.html" style="display: flex; align-items: center; gap: 12px; min-height: 64px; padding: 10px 12px 10px 16px; border-radius: 16px; background: var(--pea-tint); color: var(--pea-deep); text-decoration: none;">{SYR}'
          '<span style="flex: 1; display: flex; flex-direction: column;"><span style="font-size: 17px; line-height: 22px; font-weight: 600;">하린 · DTaP 4차 접종</span><span style="font-size: 13px; line-height: 18px;">12월 17일부터 · 2주 남았어요</span></span>'
          '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" style="flex: none;"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></path></svg></a></section>')
    assert anchor in s; s=s.replace(anchor,anchor+card,1); open(n,'w').write(s)
def children(t):
    n=f'ChildSettings{t}.dc.html'; s=open(n).read()
    if '접종·검진 일정 <span' in s: return  # 이미 넣었으면 그대로(원본 보드를 고쳐 쓰는 것이라)
    for kid,nxt in [('하린','DTaP 4차 12/17'),('도윤','B형간염 3차 2/28')]:
        i=s.index(f'font-weight: 600;">{kid}</span>'); j=s.index('</div></li>',i)+len('</div>')
        link=(f'<a href="Health{t}.dc.html" style="display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 16px 0 76px; border-top: 1px solid var(--separator); color: var(--label); text-decoration: none;">'
              f'<span style="flex: 1; font-size: 15px; line-height: 20px;">접종·검진 일정 <span style="color: var(--label-2);">· {nxt}</span></span>'
              '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style="flex: none;"><path d="M9 5l7 7-7 7" fill="none" style="stroke: var(--label-2)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></path></svg></a>')
        s=s[:j]+link+s[j:]
    s=s.replace('부모 앨범 위 아이 카드에 다음 일정이 보여요. 가족 화면에는 보이지 않아요','다음 일정이 2주 안이면 알림 탭 맨 위에 보여요. 가족 화면에는 보이지 않아요').replace('>앨범에 접종·검진 일정 보기<','>알림 탭에 다가오는 일정 보기<')
    open(n,'w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    reactions(t); children(t)
    for base,name,label in [('ParentHome','ParentHomeGlass','부모 · 떠 있는 유리 탭바(앨범, 아이 카드 뺌)'),('Settings','SettingsGlass','부모 · 떠 있는 유리 탭바(설정)'),('ParentReactions','ReactionsHealth','부모 · 알림 탭 맨 위 다가오는 일정(2주 안)')]:
        if name!='ReactionsHealth': pass
        n=f'{name}{t}.dc.html'
        if name!='ReactionsHealth': glass(f'{base}{t}.dc.html',n,'떠 있는 유리 탭바',t)
        ref=B[base+t+'.dc.html']
        if n not in d['order']: d['order'].append(n)
        x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
        B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · '+label)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
