# 대표 첫 화면(91 → 92, 사용자 2026-10-28 "마케팅 스킬 + 리서치로 업데이트" → "한 장으로 설명되면 좋겠는데" → 제목 A(단톡방)·말투 다듬기)
# 휴대폰 한 화면: 콩이·스위피·제목·한 줄·핵심 3줄·무료로 시작하기·가족 안내. 지어낸 숫자·후기 없이 제품 사실만. 라이트·다크
import os,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
KONGI='/_blob/18a8457a415dd2214e041f90295e4f10'
POINTS=['외가·친가 따로, 처음 보는 이름은 엄마아빠가 확인해요','단톡방처럼 만료되지 않고 앨범에 계속 쌓여요','할머니의 하트와 한마디가 나에게 돌아와요']
def page(t):
    """한 장(사용자 2026-10-28 "한 장으로 설명되면 좋겠는데"): 휴대폰 한 화면에 제목·핵심 3줄·시작하기·가족 안내"""
    pts=''.join(f'<li style="display: flex; align-items: flex-start; gap: 12px; text-align: left;"><span aria-hidden="true" style="flex: none; width: 24px; height: 24px; margin-top: 1px; border-radius: 50%; background: var(--pea-tint); color: var(--pea-deep); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800;">✓</span><span style="font-size: 17px; line-height: 24px;">{p}</span></li>' for p in POINTS)
    return f'''<div class="sp-t sp-{{{{theme}}}}" style="position: relative; width: 390px; height: 844px; box-sizing: border-box; background: var(--bg); color: var(--label); font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif; display: flex; flex-direction: column; overflow: hidden; word-break: keep-all;">
  <main style="flex: 1; padding: 20px 20px 0; display: flex; flex-direction: column;">
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; text-align: center;">
      <img class="sp-kongi-anim" src="{KONGI}" alt="" style="width: 88px; height: 88px; image-rendering: pixelated;">
      <p style="margin: 0; font-size: 17px; line-height: 22px; font-weight: 800; color: var(--pea-ink);">스위피</p>
      <h1 style="margin: 0; font-size: 30px; line-height: 38px; font-weight: 800; letter-spacing: -0.4px;">아기 사진,<br>단톡방에 올리고 계신가요?</h1>
      <p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">단톡방 말고 가족 앨범에 올리세요. 할머니·할아버지는 앱 설치 없이 링크로 바로 봐요.</p>
      <ul style="list-style: none; margin: 10px 0 0; padding: 18px 20px; display: flex; flex-direction: column; gap: 12px; width: 100%; box-sizing: border-box; border-radius: 18px; background: var(--surface);">{pts}</ul>
    </div>
    <div style="display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 16px 0 24px;">
      <a href="ParentLogin{t}.dc.html" style="min-height: 52px; border-radius: 12px; font-size: 17px; line-height: 22px; font-weight: 600; display: flex; align-items: center; justify-content: center; background: var(--pea); color: var(--on-pea); text-decoration: none; width: 100%; box-sizing: border-box;">무료로 시작하기</a>
      <p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">무료 5GB · 가족에게 링크를 받으셨다면 그 링크를 눌러 주세요</p>
    </div>
  </main>
</div>
'''
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    src=open(f'ParentLogin{t}.dc.html').read()
    head=src[:src.index('<div class="sp-t sp-{{theme}}"')].replace('<title>시작하기</title>','<title>스위피 첫 화면</title>')
    tail=src[src.index('</x-dc>'):]
    n=f'Landing{t}.dc.html'
    open(n,'w').write(head+page(t)+tail)
    ref=b[f'ParentLogin{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    x=max(v['x'] for v in b.values() if v['y']==ref['y'])+470 if n not in b else b[n]['x']
    b[n]=dict(ref,x=x,h=844,title=('다크' if not t else '라이트')+' · 첫 화면(sweepea.co.kr) · 소개')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
