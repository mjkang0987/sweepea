# 승인 대기 화면에 받은 사진(99, 사용자 2026-10-29 "먼저 고치기"): 안내 상자 아래 '받은 사진 N장' + 한 줄에 한 장 크게(원래 모양, 영상은 기본 재생 막대).
# 누르기·반응 없음. 묶음이 비면 사진 칸 없이 안내 글만 바꿈(속성 bundle). 아래 '다시 확인하기' 고정. 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
src=open('GrandList-Light.dc.html').read()
helmet=src[src.index('<helmet>'):src.index('</helmet>')+len('</helmet>')]
def photo(h,ph,label,video=False):
    bar=('<span aria-hidden="true" style="position: absolute; left: 12px; right: 12px; bottom: 12px; height: 36px; border-radius: 10px; background: rgba(0,0,0,0.45); display: flex; align-items: center; gap: 10px; padding: 0 12px; color: #ffffff; font-size: 13px;">'
         '<svg width="14" height="14" viewBox="0 0 24 24"><path d="M7 4l13 8-13 8z" fill="#ffffff"></path></svg><span style="flex: 1; height: 3px; border-radius: 2px; background: rgba(255,255,255,0.5);"></span>0:24</span>') if video else ''
    return f'<li style="list-style: none;"><div role="img" aria-label="{label}" style="position: relative; height: {h}px; border-radius: 16px; background: var(--{ph});">{bar}</div></li>'
def board(t):
    th='light' if t else 'dark'
    photos=photo(262,'ph-1','공원에서 웃는 하린이 사진')+photo(466,'ph-2','이유식 먹는 하린이 사진')+photo(196,'ph-1','하린이 영상, 0분 24초',True)
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>승인 대기 · 받은 사진</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
{helmet}
<main class="sp-t sp-{{{{theme}}}}" style="position: relative; width: 390px; height: 844px; box-sizing: border-box; background: var(--bg); color: var(--label); font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif; overflow: hidden;">
  <div style="height: 844px; overflow-y: auto; box-sizing: border-box; padding: 24px 16px 104px; display: flex; flex-direction: column; gap: 16px;">
    <div style="display: flex; flex-direction: column; gap: 6px;">
      <h1 style="margin: 0; font-size: 24px; line-height: 32px; font-weight: 700; letter-spacing: -0.3px;">하린이 사진</h1>
      <p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">큰이모로 들어오는 중이에요</p>
    </div>
    <section aria-labelledby="wait-h" style="padding: 14px 14px 16px; border-radius: 14px; background: var(--pea-tint); color: var(--pea-deep);">
      <h2 id="wait-h" style="margin: 0; font-size: 22px; line-height: 30px; font-weight: 700;">엄마아빠가 확인하면 다 열려요</h2>
      <p style="margin: 2px 0 0; font-size: 17px; line-height: 24px;">{{{{boxText}}}}</p>
    </section>
    <sc-if value="{{{{hasPhotos}}}}" hint-placeholder-val="{{{{true}}}}">
    <section aria-labelledby="got-h" style="display: flex; flex-direction: column; gap: 12px;">
      <h2 id="got-h" style="margin: 8px 0 0; font-size: 17px; line-height: 24px; font-weight: 700;">받은 사진 <span style="font-weight: 500; color: var(--label-2);">3장</span></h2>
      <ul style="margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px;">{photos}</ul>
    </section>
    </sc-if>
  </div>
  <div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 12px 16px 28px; background: var(--bar); backdrop-filter: blur(20px); border-top: 0.5px solid var(--separator);">
    <a href="#" style="min-height: 52px; display: flex; align-items: center; justify-content: center; border-radius: 12px; background: var(--fill); color: var(--label); text-decoration: none; font-size: 17px; line-height: 24px; font-weight: 700;">다시 확인하기</a>
  </div>
</main>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"theme":{{"editor":"enum","options":["system","light","dark"],"default":"{th}"}},"bundle":{{"editor":"enum","options":["받은 사진 있음","받은 사진 없음"],"default":"받은 사진 있음"}},"$preview":{{"width":390,"height":844}}}}'>
class Component extends DCLogic {{
renderVals() {{
const has = (this.props.bundle ?? '받은 사진 있음') === '받은 사진 있음';
return {{ theme: this.props.theme ?? '{th}', hasPhotos: has,
boxText: has ? '그동안 받은 사진은 여기서 볼 수 있어요. 3일 안에 확인하지 않으면 다시 받아야 해요.' : '그때 사진을 볼 수 있어요. 3일 안에 확인하지 않으면 다시 받아야 해요.' }};
}}
}}
</script>
</body>
</html>
'''
d=json.load(open('canvas.json')); b=d['boards']
ref=b['GrandList.dc.html']
for t in ['','-Light']:
    n=f'WaitPhotos{t}.dc.html'; open(n,'w').write(board(t))
    if n not in d['order']: d['order'].append(n)
    r=b['GrandList'+t+'.dc.html']
    x=b[n]['x'] if n in b else max(v['x'] for v in b.values() if v['y']==r['y'])+470
    b[n]=dict(r,x=x,title=('다크' if not t else '라이트')+' · 가족 · 승인 대기 · 받은 사진')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
