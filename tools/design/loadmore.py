# 아래로 내리면 60장씩 더 불러오기(88, 사용자 2026-10-28 "60장씩, 끝까지"): 목록 끝 줄 세 상태를 한 보드에 차례로
# ① 불러오는 중: 콩이 작게 + '사진 불러오는 중…'(role=status) ② 스크립트 없을 때: '사진 더 보기' 채운 알약 버튼(누르면 다음 60장 페이지)
# ③ 끝: '처음 사진까지 모두 봤어요'. 부모 홈(LoadMore)·가족 모아 보기(LoadMoreFamily, senior 글자), 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
CAP='<p style="margin: 8px 0 0; font-size: 12px; line-height: 16px; font-weight: 600; color: var(--label-3, var(--label-2)); letter-spacing: .2px;">{}</p>'
def cells(n,h=(150,110,130,150)):
    col=lambda xs:'<div style="display: flex; flex-direction: column; gap: 4px;">'+''.join(f'<div role="img" aria-label="사진 자리" style="height: {x}px; border-radius: 12px; background: var(--ph-{1+i%2});"></div>' for i,x in enumerate(xs))+'</div>'
    return f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px; align-items: start;">{col(h[:n//2])}{col(h[n//2:n])}</div>'
def rows(big):
    f=17 if big else 15; lh=24 if big else 20; k=40 if big else 32; btn=56 if big else 52; bf=21 if big else 17  # 가족은 senior 글자(캡션 17·버튼 21)
    load=f'<p style="margin: 0; min-height: 64px; display: flex; align-items: center; justify-content: center; gap: 10px; font-size: {f}px; line-height: {lh}px; color: var(--label-2);"><img src="/_blob/18a8457a415dd2214e041f90295e4f10" width="{k}" height="{k}" alt="" style="width: {k}px; height: {k}px; image-rendering: pixelated;">사진 불러오는 중…</p>'
    more=f'<a href="#" style="min-height: {btn}px; display: flex; align-items: center; justify-content: center; border-radius: 999px; background: var(--fill); color: var(--pea-deep); text-decoration: none; font-size: {bf}px; line-height: 24px; font-weight: 700;">사진 더 보기</a>'
    end=f'<p style="margin: 0; min-height: 64px; display: flex; align-items: center; justify-content: center; gap: 10px; font-size: {f}px; line-height: {lh}px; color: var(--label-2);"><img src="/_blob/18a8457a415dd2214e041f90295e4f10" width="{k}" height="{k}" alt="" style="width: {k}px; height: {k}px; image-rendering: pixelated;">처음 사진까지 모두 봤어요</p>'
    return CAP.format('① 내려오면 저절로 · 불러오는 중')+load+CAP.format('② 스크립트가 없을 때 · 누르면 다음 60장')+more+CAP.format('③ 더 없을 때')+end
def board(src,big,title):
    s=open(src).read()
    s=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',s,count=1)
    i=s.find('<main'); i=s.find('>',i)+1; j=s.find('</main>')
    head=(f'<h2 style="margin: 0; font-size: {24 if big else 22}px; line-height: 30px; font-weight: 700;">2024년 5월 1일 <span style="font-weight: 500; color: var(--label-2); font-size: {19 if big else 15}px;">· 4장</span></h2>' if big else
          '<div style="display: flex; align-items: baseline; justify-content: space-between;"><h2 style="margin: 0; font-size: 22px; line-height: 28px; font-weight: 700; letter-spacing: -0.3px;">2024년 5월</h2><span style="font-size: 13px; line-height: 18px; color: var(--label-2);">하린 생후 0개월 · 사진 4</span></div>')
    s=s[:i]+'\n    '+head+cells(4)+rows(big)+'\n  '+s[j:]
    if big:  # 가족 화면: 탭바·사진 추가하기 없음
        s=re.sub(r'\s*<a href="ParentUpload[^"]*" class="sp-glass-tint".*?</a>','',s,count=1,flags=re.S)
        s=re.sub(r'\s*<nav aria-label="탭".*?</nav>','',s,count=1,flags=re.S)
    return s
d=json.load(open('canvas.json')); b=d['boards']
for name,big,label,base in [('LoadMore',False,'부모 · 앨범 끝 · 더 불러오기','ParentHome'),('LoadMoreFamily',True,'가족 · 모아 보기 끝 · 더 불러오기','ParentHome')]:
    for t in ['','-Light']:
        n=name+t+'.dc.html'
        open(n,'w').write(board(base+t+'.dc.html',big,('앨범 끝' if not big else '모아 보기 끝')+' · 더 불러오기'))
        ref=b[base+t+'.dc.html']
        if n not in d['order']: d['order'].append(n)
        x=max(v['x'] for v in b.values() if v['y']==ref['y'])+470 if n not in b else b[n]['x']
        b[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · '+label)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
