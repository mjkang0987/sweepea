# 영상 줄이기(디자인 152, 사용자 2026-10-27 "네 추천대로"): 무료는 폰에서 1080p로 줄인 사본만 올린다.
# 고르면 바로 줄이고 상태 칸에 '영상 줄이는 중… 2 / 3 · 40%' + 진행 막대, 아래에 '화면을 켜 두세요'. 줄이는 동안 버튼은 잠김.
# 올릴 때도 '올리는 중… 2 / 3' + 진행 막대(사용자 "프로그래스바 둘 다"). 막대는 묶음 전체 기준.
# 퍼센트 글은 영상 하나의 진행일 때만(줄이는 중·큰 영상 나눠 올리기). 사진은 나눈 숫자와 같아 뺌(사용자 2026-10-27 "사진 업로드에서 퍼센트는 빼줘")
# 원본·줄임 안내(사용자 "원본과 압축에 관한 고지 제대로"): 크기 칸 아래에 늘 보임
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
src=open('ParentPhoto.dc.html').read()
head=src[:src.index('<div class="sp-t sp-{{theme}}"')].replace('<title>사진 정보 수정</title>','<title>사진 올리기 · 영상 줄이는 중</title>')
tail=src[src.index('</x-dc>'):]
CHIP='<label style="display: inline-flex; align-items: center; gap: 6px; min-height: 40px; padding: 0 12px; border-radius: 999px; background: var(--pea-tint); color: var(--pea-deep); font-weight: 600; font-size: 15px; opacity: .5;"><input type="checkbox" checked disabled style="width: 18px; height: 18px; margin: 0; accent-color: var(--pea);">{}</label>'
def cell(bg,cover=False,video=False):
    b='3px solid var(--pea)' if cover else '0'
    v='<span style="position: absolute; right: 6px; bottom: 6px; padding: 1px 6px; border-radius: 6px; background: rgba(0,0,0,.55); color: #fff; font-size: 12px; line-height: 18px; font-weight: 600;">0:22</span>' if video else ''
    return f'<li style="position: relative; aspect-ratio: 1; border-radius: 10px; box-sizing: border-box; border: {b}; background: var({bg});">{v}</li>'
NOTE='''    <p style="margin: -4px 0 0; font-size: 15px; line-height: 21px; color: var(--label-2);">사진·영상은 앨범에서 보기 좋은 크기로 줄여서 올려요(영상은 1080p, 줄일 수 없으면 그대로). <strong style="color: var(--label); font-weight: 600;">스위피는 원본을 따로 보관하지 않으니 원본은 폰에서 지우지 마세요.</strong></p>\n'''
def status(text,hint,pct):
    h=f'<p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">{hint}</p>' if hint else ''
    return f'''    <div style="display: flex; flex-direction: column; gap: 8px;">
      <p role="status" style="margin: 0; padding: 12px 16px; border-radius: 12px; background: var(--pea-tint); color: var(--pea-deep); font-size: 17px; line-height: 24px; font-weight: 700; font-variant-numeric: tabular-nums;">{text}</p>
      <div role="progressbar" aria-label="진행률" aria-valuenow="{pct}" style="height: 6px; border-radius: 999px; background: var(--fill); overflow: hidden;"><div style="width: {pct}%; height: 100%; border-radius: 999px; background: var(--pea);"></div></div>
      {h}
    </div>
'''
def page(STATUS,SIZE):
  return f'''<div class="sp-t sp-{{{{theme}}}}" style="width: 390px; height: 844px; box-sizing: border-box; background: var(--bg); color: var(--label); font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif; display: flex; flex-direction: column; overflow: hidden; word-break: keep-all;">
  <main style="flex: 1; min-height: 0; padding: 20px 20px 0; display: flex; flex-direction: column; gap: 16px; overflow: hidden;">
    <div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; min-height: 44px; margin-top: 4px;">
      <a href="ParentHome.dc.html" style="justify-self: start; min-height: 44px; display: flex; align-items: center; color: var(--pea-ink); text-decoration: none; font-size: 17px; line-height: 22px;">취소</a>
      <h1 style="margin: 0; font-size: 17px; line-height: 22px; font-weight: 600;">사진·영상 3장</h1>
      <span></span>
    </div>
    <div style="min-height: 56px; display: flex; align-items: center; justify-content: center; border: 1.5px dashed var(--separator); border-radius: 14px; color: var(--pea-ink); font-size: 17px; font-weight: 700; opacity: .5;">사진·영상 고르기</div>
    <ul style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 4px;">{cell('--ph-1',True)}{cell('--ph-2')}{cell('--ph-1')}</ul>
    <ul style="list-style: none; margin: 0; padding: 0; border-radius: 16px; overflow: hidden; background: var(--surface);">
      <li style="padding: 12px 16px;"><p style="margin: 0 0 10px; font-size: 17px;">아이</p>{CHIP.format('하린')}</li>
      <li style="border-top: 1px solid var(--separator); padding: 12px 16px;"><p style="margin: 0 0 10px; font-size: 17px;">보여줄 그룹</p><div style="display: flex; gap: 8px;">{CHIP.format('외가')}{CHIP.format('친가')}</div></li>
      <li style="border-top: 1px solid var(--separator); display: flex; align-items: center; min-height: 52px; padding: 0 16px;"><span style="flex: 1; font-size: 17px;">크기</span><span style="color: var(--label-2); font-size: 15px;">{SIZE}</span></li>
    </ul>
{NOTE}{STATUS}    <button type="button" disabled style="min-height: 52px; border: 0; border-radius: 14px; background: var(--kakao); color: var(--kakao-ink); font-family: inherit; font-size: 17px; font-weight: 700; opacity: .4;">올리고 카톡으로 보내기</button>
    <button type="button" disabled style="min-height: 44px; border: 0; background: transparent; color: var(--pea-ink); font-family: inherit; font-size: 17px; font-weight: 600; opacity: .4;">보내지 않고 올리기만</button>
  </main>
</div>
'''
BOARDS={'UploadShrink':(page(status('영상 줄이는 중… 2 / 3 · 40%','영상을 보기 좋은 크기로 줄이고 있어요. 다 줄일 때까지 이 화면을 켜 두세요.',40),'줄이는 중'),'영상 줄이는 중'),
 'UploadSending':(page(status('올리는 중… 2 / 3','',65),'보기 좋은 크기 · 41.2MB'),'올리는 중')}
d=json.load(open('canvas.json')); b=d['boards']
ref=b['ParentPhoto.dc.html']; refL=b['ParentPhoto-Light.dc.html']
for name,(body,label) in BOARDS.items():
  for t,r in [('',ref),('-Light',refL)]:
    n=name+t+'.dc.html'
    s=head.replace('영상 줄이는 중',label)+body+tail
    if t: s=s.replace('"default":"dark"','"default":"light"').replace("?? 'dark'","?? 'light'")
    open(n,'w').write(s)
    if n not in b:
        x=max(v['x'] for v in b.values() if v['y']==r['y'])+470
        d['order'].append(n); b[n]=dict(r,x=x,title=('다크' if not t else '라이트')+' · 부모 · 올리기 · '+label)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
