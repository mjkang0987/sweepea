# 대표 첫 화면(91 → 92 문구, 사용자 2026-10-28 "마케팅 스킬 + 리서치로 업데이트" → "한 장으로 설명되면 좋겠는데"): 휴대폰 한 화면 소개
# 세 박자: 지금 불편(이런 적 있으세요?) → 바뀐 모습(좋은 점) → 시작 방법(이렇게 써요·시작하기). 지어낸 숫자·후기 없이 제품 사실만
# 머리: 콩이·스위피·제목(검색어 '아기 사진')·설명·'무료로 시작하기'·가족 안내 / 불편 3 / 3단계 / 좋은 점 3(소개 그림 카드) / 자주 묻는 질문 / 마지막 시작하기 / 바닥글
# 휴대폰 390 기준, 넓은 화면은 같은 줄을 가운데로(보드 없음). 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
KONGI='/_blob/18a8457a415dd2214e041f90295e4f10'
PAINS=['단톡방에 올린 사진이 만료돼서 다시 보내 달라는 연락을 받았어요','앱을 깔아 드렸는데 비밀번호를 잊으셔서 못 보세요','시댁과 친정에 같은 사진을 따로따로 보내요']
STEPS=[('사진 올리기','폰에서 고르면 보기 좋은 크기로 줄여서 올려요. 영상도 돼요.'),
       ('카톡으로 링크 보내기','외가·친가처럼 볼 사람을 나눠서 보낼 수 있어요.'),
       ('가족은 누르면 끝','처음 한 번만 이름과 가족 비밀번호를 넣으면 다음부터는 바로 열려요.')]
FEATS=[('할머니 휴대폰에 앱이 없어도 돼요','카톡 링크만 누르면 바로 열려요.<br>글씨도 크게 키워서 볼 수 있어요.'),
       ('누가 볼지는 엄마아빠가 정해요','외가·친가처럼 그룹을 나누고,<br>처음 들어오는 사람은 승인해야 봐요.'),
       ('하트와 한마디가 돌아와요','할머니가 남긴 하트와 한마디를 모아 보고,<br>콩이도 아이 나이에 맞춰 함께 자라요.')]
FAQ=[('조부모님 휴대폰에 앱을 깔아야 하나요?','아니요. 카톡이나 문자로 받은 링크를 누르면 바로 열려요. 처음 한 번만 이름과 가족 비밀번호를 넣어요.'),
     ('링크만 있으면 아무나 볼 수 있나요?','아니요. 처음 들어오는 사람은 엄마아빠가 승인해야 사진을 볼 수 있어요. 그룹마다 볼 수 있는 사진도 따로 정해요.'),
     ('사진은 얼마나 보관되나요?','지우기 전까지 계속 남아요. 무료로 5GB까지 올릴 수 있고, 다 차면 새로 올리기만 멈추고 가족은 계속 볼 수 있어요.'),
     ('원본 화질로 올라가나요?','앨범에서 보기 좋은 크기로 줄여서 올려요(영상은 1080p). 스위피는 원본을 따로 보관하지 않으니 원본은 폰에 남겨 두세요.'),
     ('돈이 드나요?','무료로 시작할 수 있어요. 저장 공간 5GB까지 무료예요.')]
def art(f):
    """소개 보드의 그림 카드(section 안 첫 div)를 그대로"""
    s=open(f).read(); i=s.index('<section'); i=s.index('>',i)+1
    j=s.index('<div style="display: flex; flex-direction: column; gap: 10px;">\n        <h1',i)
    return s[i:j].strip()
H2='margin: 0; font-size: 22px; line-height: 28px; font-weight: 700; letter-spacing: -0.3px;'
SEC='display: flex; flex-direction: column; gap: 20px; padding: 40px 0; border-top: 1px solid var(--separator);'
BTN='<a href="ParentLogin{t}.dc.html" style="min-height: 52px; border-radius: 12px; font-size: 17px; line-height: 22px; font-weight: 600; display: flex; align-items: center; justify-content: center; background: var(--pea); color: var(--on-pea); text-decoration: none; width: 100%; max-width: 360px; box-sizing: border-box;">무료로 시작하기</a>'
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
