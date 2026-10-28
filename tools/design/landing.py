# 대표 첫 화면(91, 사용자 2026-10-28 "루트에 컨텐츠 노출되는 걸로", 서치 콘솔 등록용): 처음 온 사람이 보는 한 장짜리 소개
# 위: 콩이·스위피·한 줄 소개(로그인 보드와 같음) + '시작하기'(엄마아빠) + 가족 안내 한 줄(링크 받은 조부모님)
# 가운데: 소개 3장(ParentIntro1~3)의 그림 카드·제목·설명을 차례로(제목은 h2, 28→22px title-2). 아래: '시작하기' 한 번 더 + 바닥글
# 휴대폰 390 기준, 넓은 화면은 같은 줄을 가운데 40rem로(보드 없음). 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
KONGI='/_blob/18a8457a415dd2214e041f90295e4f10'
def art(f):
    """소개 보드의 그림 카드(section 안 첫 div)를 그대로"""
    s=open(f).read(); i=s.index('<section'); i=s.index('>',i)+1
    j=s.index('<div style="display: flex; flex-direction: column; gap: 10px;">\n        <h1',i)
    return s[i:j].strip()
def text(f):
    s=open(f).read()
    h=re.search(r'<h1[^>]*>(.*?)</h1>',s).group(1); p=re.search(r'<h1.*?</h1>\s*<p[^>]*>(.*?)</p>',s,re.S).group(1)
    return h,p
BTN='<a href="ParentLogin{t}.dc.html" style="min-height: 52px; border-radius: 12px; font-size: 17px; line-height: 22px; font-weight: 600; display: flex; align-items: center; justify-content: center; background: var(--pea); color: var(--on-pea); text-decoration: none; width: 100%; max-width: 360px; box-sizing: border-box;">시작하기</a>'
def page(t):
    feats=''
    for n in (1,2,3):
        f=f'ParentIntro{n}{t}.dc.html'; h,p=text(f)
        feats+=f'''
    <section aria-labelledby="f{n}" style="display: flex; flex-direction: column; align-items: center; gap: 24px; text-align: center; padding: 40px 0; border-top: 1px solid var(--separator);">
      {art(f)}
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <h2 id="f{n}" style="margin: 0; font-size: 22px; line-height: 28px; font-weight: 700; letter-spacing: -0.3px;">{h}</h2>
        <p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">{p}</p>
      </div>
    </section>'''
    return f'''<div class="sp-t sp-{{{{theme}}}}" style="position: relative; width: 390px; box-sizing: border-box; background: var(--bg); color: var(--label); font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif; word-break: keep-all;">
  <main style="padding: 20px 20px 0; display: flex; flex-direction: column;">
    <header style="display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; padding: 72px 0 48px;">
      <img class="sp-kongi-anim" src="{KONGI}" alt="" style="width: 128px; height: 128px; image-rendering: pixelated;">
      <h1 style="margin: 0; font-size: 34px; line-height: 41px; font-weight: 800; letter-spacing: -0.02em;">스위피</h1>
      <p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">카톡으로 보내고, 설치 없이 보고,<br>사라지지 않는 가족 앨범</p>
      <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; width: 100%; margin-top: 12px;">
        {BTN.format(t=t)}
        <p style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">가족에게 링크를 받으셨나요? 받은 링크를 눌러 주세요</p>
      </div>
    </header>{feats}
    <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 40px 0 32px; border-top: 1px solid var(--separator);">
      {BTN.format(t=t)}
    </div>
    <footer style="padding: 20px 0 32px; border-top: 1px solid var(--separator); text-align: center; font-size: 13px; line-height: 18px; color: var(--label-2);">스위피 · sweepea.co.kr</footer>
  </main>
</div>
'''
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    src=open(f'ParentLogin{t}.dc.html').read()
    head=src[:src.index('<div class="sp-t sp-{{theme}}"')].replace('<title>시작하기</title>','<title>스위피 첫 화면</title>')
    tail=src[src.index('</x-dc>'):].replace('"height":844','"height":2200')
    n=f'Landing{t}.dc.html'
    open(n,'w').write(head+page(t)+tail)
    ref=b[f'ParentLogin{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    x=max(v['x'] for v in b.values() if v['y']==ref['y'])+470 if n not in b else b[n]['x']
    b[n]=dict(ref,x=x,h=2200,title=('다크' if not t else '라이트')+' · 첫 화면(sweepea.co.kr) · 소개')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
