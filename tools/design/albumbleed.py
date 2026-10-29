# 앨범 위 고정 머리 + 사진 좌우 꽉(사용자 2026-10-29, 아이폰 사진 앱 보관함 캡처 "헤더 고정 영역 디자인 맞춰 주고, 사진 영역은 좌우 여백 없이").
# ParentHomeGlass에서: 맨 위 '앨범' 큰 제목 + 작은 줄(사진·영상 수)을 사진 위에 떠 있는 머리로(화면색 → 투명 그라데이션 + 흐림),
# (2026-10-29 "fixed 영역에 흰 배경 뭐야?" → 화면색 75% 막 + 흐림 20px, 작은 줄도 진한 글자)
# 사진 묶음은 좌우 여백 0·간격 2px·모서리 0. 달 제목·안내 카드·아이 고르기는 여백 그대로
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
HEAD=('<header style="position: absolute; z-index: 5; top: 0; left: 0; right: 0; padding: 54px 20px 22px; '
      'background: linear-gradient(color-mix(in srgb, var(--bg) 75%, transparent) calc(100% - 22px), transparent);">'
      '<div aria-hidden="true" style="position: absolute; inset: 0; z-index: -1; -webkit-backdrop-filter: blur(20px); backdrop-filter: blur(20px); '
      '-webkit-mask-image: linear-gradient(#000 calc(100% - 22px), transparent); mask-image: linear-gradient(#000 calc(100% - 22px), transparent);"></div>'
      '<h1 style="margin: 0; font-size: 34px; line-height: 41px; font-weight: 700; letter-spacing: -0.4px;">앨범</h1>'
      '<p style="margin: 2px 0 0; font-size: 15px; line-height: 20px; color: var(--label);">사진 1,284 · 영상 37</p></header>')
def bleed(t):
    s=open(f'ParentHomeGlass{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>앨범 고정 머리</title>',s,count=1)
    # 맨 위 버튼 줄·제목 → 떠 있는 머리(main 밖, 사진 위)
    s=re.sub(r'\s*<div style="display: flex; justify-content: flex-end; gap: 8px;">.*?</div>\s*<h1 [^>]*>앨범</h1>','',s,count=1,flags=re.S)
    s=s.replace('<main style="flex: 1; min-height: 0; padding: 20px 20px 0;','<main style="flex: 1; min-height: 0; padding: 124px 0 0;',1)
    s=s.replace('<main ',HEAD+'\n  <main ',1)
    # 안내 카드·아이 고르기·달 제목은 좌우 20px 그대로
    for pat in [r'(<a href="Family[^"]*\.dc\.html" style=")',r'(<a href="SendSetup[^"]*\.dc\.html" style=")',r'(<div role="status" style=")',r'(<div role="alert" style=")',
r'(<div style="display: flex; align-items: baseline; justify-content: space-between;)']:
        s=re.sub(pat,lambda m: m.group(1).replace('style="','style="margin-inline: 20px; ') if m.group(1).endswith('style="') else m.group(1).replace('style="','style="margin-inline: 20px; '),s,count=1)
    s=s.replace('<fieldset style="margin: 0;','<fieldset style="margin: 0 20px;',1)
    # 사진: 간격 2px, 모서리 0
    s=s.replace('grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px;','grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2px;')
    s=s.replace('display: flex; flex-direction: column; gap: 4px;','display: flex; flex-direction: column; gap: 2px;')
    s=re.sub(r'(role="img"[^>]*?)border-radius: 12px; ',r'\1',s)
    open(f'ParentHomeBleed{t}.dc.html','w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    bleed(t)
    n=f'ParentHomeBleed{t}.dc.html'; ref=B[f'ParentHomeGlass{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
    B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · 부모 · 앨범 고정 머리 + 사진 좌우 꽉')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
