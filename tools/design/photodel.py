# 사진 지우기 확인 레이어(PhotoDeleteLayer, -Light): 사진 정보 수정 화면 위에 어둡게 + 가운데 상자
import os,json
os.chdir('/home/claude/sweepea/tools/canvas/project')
L='''  <div class="sp-layer-scrim" aria-hidden="true" style="position: absolute; inset: 0; z-index: 50; background: rgba(0,0,0,0.45);"></div>
  <dialog class="sp-layer-box" open aria-labelledby="pd-t" aria-describedby="pd-d" style="position: absolute; z-index: 51; left: 20px; right: 20px; top: 50%; transform: translateY(-50%); margin: 0; width: auto; box-sizing: border-box; padding: 24px 20px 20px; border: 0; border-radius: 22px; background: var(--surface); color: var(--label); display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; word-break: keep-all;">
    <h2 id="pd-t" style="margin: 0; font-size: 20px; line-height: 26px; font-weight: 700;">이 사진을 지울까요?</h2>
    <p id="pd-d" style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">가족 화면에서도 바로 사라지고, 남긴 반응과 한마디도 같이 지워져요. 되돌릴 수 없어요.</p>
    <div style="align-self: stretch; display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--danger); color: var(--bg); font-family: inherit; font-size: 17px; font-weight: 600;">지우기</button>
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">취소</button>
    </div>
  </dialog>
'''
for t in ['','-Light']:
    s=open('ParentPhoto'+t+'.dc.html').read()
    import re
    s=re.sub(r'<title>.*?</title>','<title>사진 지우기 확인</title>',s,count=1)
    k=s.rfind('</x-dc>'); k=s.rfind('</div>',0,k)
    s=s[:k]+L+s[k:]
    open('PhotoDeleteLayer'+t+'.dc.html','w').write(s)
d=json.load(open('canvas.json')); b=d['boards']
x=b['ParentPhoto.dc.html']; xl=b['ParentPhoto-Light.dc.html']
print(x,xl)
b['PhotoDeleteLayer.dc.html']=dict(x,x=x['x']+x['w']+80,title=x['title'].replace('사진 정보 수정','사진 지우기 확인') if '사진 정보 수정' in x['title'] else x['title']+' · 지우기 확인')
b['PhotoDeleteLayer-Light.dc.html']=dict(xl,x=xl['x']+xl['w']+80,title=xl['title'].replace('사진 정보 수정','사진 지우기 확인') if '사진 정보 수정' in xl['title'] else xl['title']+' · 지우기 확인')
for k in ['PhotoDeleteLayer.dc.html','PhotoDeleteLayer-Light.dc.html']: print(k,b[k])
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
