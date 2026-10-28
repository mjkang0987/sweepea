# 대표 첫 화면(91 → 92, 사용자 2026-10-28 "마케팅 스킬 + 리서치로 업데이트" → "한 장으로 설명되면 좋겠는데" → 제목 A(단톡방)·말투 다듬기)
# 휴대폰 한 화면: 콩이·스위피·제목·두 줄·서비스 화면(할머니가 보는 앨범)·짧은 낱말 셋·무료로 시작하기·가족 안내. 지어낸 숫자·후기 없이 제품 사실만. 라이트·다크
import os,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
# 콩이는 캔버스 파일 주소(/_blob/…)가 새 보드에서 안 열려 깨졌다(사용자 '이미지 깨져') → 앱의 public/kongi.svg를 그대로 넣는다
import base64
# 지금 폴더는 tools/canvas/project
KONGI='data:image/svg+xml;base64,'+base64.b64encode(open(os.path.join('..','..','..','public','kongi.svg'),'rb').read()).decode()
# 그림은 32칸의 아래쪽(x 9–23, y 13–32)에만 있어 가운데 놓아도 처져 보인다 → 사진 칸에선 그린 부분만 잘라 쓴다(여백 1칸)
_svg=open(os.path.join('..','..','..','public','kongi.svg')).read().replace('viewBox="0 0 32 32"','viewBox="8 12 16 21"',1)
KONGI_CROP='data:image/svg+xml;base64,'+base64.b64encode(_svg.encode()).decode()
# 이모지 글꼴(앱 ReactRow와 같음). 작은따옴표가 든 글을 f문자열 밖에 둔다
EF="font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;"
CHIPS=['앱 설치 없이','외가·친가 따로','지우기 전엔 그대로']
def page(t):
    """한 장(사용자 2026-10-28 "설명문구가 너무 구리다" → 말 대신 장면): 제목 + 두 줄 + 서비스 화면(할머니가 보는 앨범) + 짧은 낱말 셋 + 시작하기"""
    chips=''.join(f'<li style="padding: 6px 12px; border-radius: 999px; background: var(--surface); font-size: 14px; line-height: 20px; font-weight: 600; color: var(--label-2); white-space: nowrap;">{c}</li>' for c in CHIPS)
    # 사진 자리엔 콩이(사용자 '아기 사진 비우지 말고 콩이 넣어 줘'). 서비스 화면(사용자 "카톡 대화 장면 말고 서비스 화면 보여 주는 게 맞지 않나?"): 할머니가 링크를 누르면 보는 앨범(GrandHome 넘겨 보기)을 휴대폰 틀에
    # 실제 서비스 화면(사용자 '실제 서비스 UI, 좌우에 이전·다음 사진'): GrandHome 넘겨 보기를 줄여서 — 가운데 카드 + 양옆 비스듬한 이전·다음 카드, n/12, 눌러서 바로 보내기, 한마디.
    # 폭 280 휴대폰, 내용은 다 보이고 아래 테두리만 배경색으로 흐려 자름(사용자 '하단 라인 부분 정도만'). 몸체는 검정 그대로, 옆면 얇은 금속선 + 뒤 빛(다크에서 배경에 묻히지 않게, 사용자 '테두리가 밝아지면 핸드폰이 아니잖어')
    chip=lambda e,n='',on=False: f'<span style="flex: 1; min-width: 0; min-height: 30px; border-radius: 15px; background: {"var(--pea-tint)" if on else "var(--surface)"}; {"box-shadow: inset 0 0 0 1.5px var(--pea); color: var(--pea-deep);" if on else ""} display: flex; align-items: center; justify-content: center; gap: 2px; font-size: 11px; font-weight: 700;"><span style="{EF} font-size: 13px;">{e}</span>{n}</span>'
    side=lambda left,rot,origin: f'<span style="position: absolute; top: 12px; left: {left}px; width: 176px; height: 196px; border-radius: 14px; overflow: hidden; background: var(--surface); transform: perspective(700px) rotateY({rot}deg) scale(0.86); transform-origin: {origin} center; opacity: 0.5;"><span style="display: block; height: 160px; background: var(--ph-2);"></span></span>'
    chat=f'''<div aria-hidden="true" style="position: relative; width: 340px; padding: 26px 30px 0; margin-top: -22px; box-sizing: border-box; overflow: hidden;">
        <div style="box-sizing: border-box; padding: 9px 9px 0; border-radius: 42px 42px 0 0; background: #1d1d1f; box-shadow: 0 0 0 1.5px #3a3a3c, 0 0 0 2.5px #8e8e93, 0 -4px 26px var(--phone-glow);">
          <div style="border-radius: 34px 34px 0 0; overflow: hidden; background: var(--bg); padding: 20px 12px 22px; display: flex; flex-direction: column; gap: 8px; text-align: left;">
            <div style="display: flex; flex-direction: column; gap: 1px;"><strong style="font-size: 17px; line-height: 22px; font-weight: 800;">하린이 새 사진 12장</strong><span style="font-size: 11px; line-height: 15px; color: var(--label-2);">오늘 엄마가 올렸어요</span></div>
            <div style="position: relative; height: 220px; margin: 0 -12px; overflow: hidden;">
              {side(-108,18,'right')}
              {side(218,-18,'left')}
              <span style="position: absolute; top: 0; left: 43px; width: 176px; height: 220px; border-radius: 14px; overflow: hidden; background: var(--surface); box-shadow: 0 6px 16px rgba(0,0,0,0.16), 0 2px 5px rgba(0,0,0,0.08); display: flex; flex-direction: column;">
                <span style="flex: 1; background: linear-gradient(160deg, var(--pea-tint), var(--ph-2)); display: flex; align-items: center; justify-content: center;"><img class="sp-kongi-anim" src="{KONGI_CROP}" alt="" style="width: 84px; height: 110px; image-rendering: pixelated;"></span>
                <span style="flex: none; padding: 5px 10px; font-size: 11px; line-height: 15px; font-weight: 500; color: var(--label-2);">생후 13개월 · 10월 21일</span>
              </span>
            </div>
            <p style="margin: 0; text-align: center; font-size: 11px; line-height: 15px; color: var(--label-2);"><strong style="color: var(--label);">1</strong> / 12 · 옆으로 밀거나 옆 사진을 누르세요</p>
            <span style="font-size: 11px; line-height: 15px; color: var(--label-2);">눌러서 바로 보내기</span>
            <div style="display: flex; gap: 4px;">{chip('❤️',' 3',True)}{chip('👍',' 1')}{chip('😊')}{chip('😭')}{chip('✨')}</div>
            <div style="display: flex; gap: 5px;"><span style="flex: 1; min-height: 32px; border-radius: 9px; box-shadow: inset 0 0 0 1px var(--separator); display: flex; align-items: center; padding: 0 10px; font-size: 11px; color: var(--label-2);">하린이에게 한마디</span><span style="min-height: 32px; padding: 0 12px; border-radius: 9px; background: var(--pea); color: var(--on-pea); display: flex; align-items: center; font-size: 11px; font-weight: 700;">보내기</span></div>
          </div>
        </div>
        <div style="position: absolute; left: -2px; right: -2px; bottom: 0; height: 22px; background: linear-gradient(to bottom, transparent, var(--bg));"></div>
      </div>'''
    return f'''<div class="sp-t sp-{{{{theme}}}}" style="position: relative; width: 390px; height: 844px; box-sizing: border-box; background: var(--bg); color: var(--label); font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif; display: flex; flex-direction: column; overflow: hidden; word-break: keep-all;">
  <main style="flex: 1; padding: 20px 20px 0; display: flex; flex-direction: column;">
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; text-align: center;">
      <p style="margin: 0; display: flex; align-items: center; gap: 6px; font-size: 17px; line-height: 22px; font-weight: 800; color: var(--pea-ink);"><img class="sp-kongi-anim" src="{KONGI}" alt="" style="width: 28px; height: 28px; image-rendering: pixelated;">스위피</p>
      <h1 style="margin: 0; font-size: 28px; line-height: 36px; font-weight: 800; letter-spacing: -0.4px;">아기 사진,<br>단톡방에 올리고 계신가요?</h1>
      <p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">링크 하나만 보내세요.<br>할머니는 누르기만 하면 돼요.</p>
      {chat}
      <ul style="list-style: none; margin: 2px 0 0; padding: 0; display: flex; flex-wrap: wrap; justify-content: center; gap: 6px;">{chips}</ul>
    </div>
    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 0 22px;">
      <a href="ParentLogin{t}.dc.html" style="min-height: 52px; border-radius: 12px; font-size: 17px; line-height: 22px; font-weight: 600; display: flex; align-items: center; justify-content: center; background: var(--pea); color: var(--on-pea); text-decoration: none; width: 100%; box-sizing: border-box;">무료로 시작하기</a>
      <p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">5GB까지 무료</p>
      <p style="margin: 4px 0 0; font-size: 15px; line-height: 21px; color: var(--label-2);">링크 받으셨나요? 받은 링크를 눌러 주세요</p>
    </div>
  </main>
</div>
'''
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    src=open(f'ParentLogin{t}.dc.html').read()
    head=src[:src.index('<div class="sp-t sp-{{theme}}"')].replace('<title>시작하기</title>','<title>스위피 첫 화면</title>')
    # 휴대폰 뒤 빛: 라이트는 그림자, 다크는 민트 빛(검은 배경에 검은 몸체가 묻히지 않게)
    head=head.replace('</style>','.sp-t{--phone-glow:rgba(0,0,0,0.16)}.sp-dark{--phone-glow:rgba(45,212,191,0.30)}@media (prefers-color-scheme: dark){.sp-system{--phone-glow:rgba(45,212,191,0.30)}}\n</style>',1)
    tail=src[src.index('</x-dc>'):]
    n=f'Landing{t}.dc.html'
    open(n,'w').write(head+page(t)+tail)
    ref=b[f'ParentLogin{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    x=max(v['x'] for v in b.values() if v['y']==ref['y'])+470 if n not in b else b[n]['x']
    b[n]=dict(ref,x=x,h=844,title=('다크' if not t else '라이트')+' · 첫 화면(sweepea.co.kr) · 소개')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
