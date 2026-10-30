# 그룹 상세 그 자리에서(디자인 150): 주소 보내기 뒤 링크 카드가 이 화면에(GroupLinkCard), 주소 다시 만들기 확인 레이어(GroupResetLayer)
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
CARD='''<section aria-labelledby="gl-t" style="flex: none; padding: 16px; border-radius: 16px; background: var(--surface); display: flex; flex-direction: column; gap: 12px;">
      <h2 id="gl-t" style="margin: 0; font-size: 17px; line-height: 22px; font-weight: 700;">외가 링크를 만들었어요</h2>
      <label for="gl-u" style="font-size: 15px; font-weight: 700;">주소(길게 눌러 복사)</label>
      <input id="gl-u" type="url" readonly value="https://sweepea.co.kr/i/Hr7kQ2mP" style="box-sizing: border-box; width: 100%; height: 52px; padding: 0 16px; border: 1.5px solid var(--label-2); border-radius: 12px; background: var(--bg); color: var(--label); font-family: inherit; font-size: 17px;">
      <a href="#" style="min-height: 52px; border-radius: 12px; background: var(--pea); color: var(--on-pea); display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 17px; font-weight: 600;">문자로 보내기</a>
      <p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">3일 안에는 새 이름으로도 들어올 수 있어요. 이미 등록된 이름은 언제든 들어와요.</p>
    </section>
    '''
def layer(t,d,ok):
    return f'''  <div aria-hidden="true" style="position: absolute; inset: 0; z-index: 50; background: rgba(0,0,0,0.45);"></div>
  <dialog open aria-labelledby="gr-t" aria-describedby="gr-d" style="position: absolute; z-index: 51; left: 20px; right: 20px; top: 50%; transform: translateY(-50%); margin: 0; width: auto; box-sizing: border-box; padding: 24px 20px 20px; border: 0; border-radius: 22px; background: var(--surface); color: var(--label); display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; word-break: keep-all;">
    <h2 id="gr-t" style="margin: 0; font-size: 20px; line-height: 26px; font-weight: 700;">{t}</h2>
    <p id="gr-d" style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">{d}</p>
    <div style="align-self: stretch; display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--danger); color: var(--bg); font-family: inherit; font-size: 17px; font-weight: 600;">{ok}</button>
      <button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">취소</button>
    </div>
  </dialog>
'''
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    base=open('GroupDetail'+t+'.dc.html').read()
    if '--danger' not in base:
        base=base.replace('--bar:rgba(255,255,255,0.92)','--bar:rgba(255,255,255,0.92);--danger:#d70015',1).replace('--bar:rgba(22,22,24,0.92)','--bar:rgba(22,22,24,0.92);--danger:#ff6961',2)
    # 링크 카드: '카톡으로 보내기' 줄이 든 목록 바로 아래
    i=base.index('카톡으로 보내기'); j=base.index('</ul>',i)+len('</ul>')
    s=base[:j]+'\n    '+CARD+base[j:]
    s=re.sub(r'<title>(.*?)</title>',lambda m:f'<title>{m.group(1)} · 링크 카드</title>',s,count=1)
    n1='GroupLinkCard'+t+'.dc.html'; open(n1,'w').write(s)
    k=base.rfind('</x-dc>'); k=base.rfind('</div>',0,k)
    s2=base[:k]+layer('외가 주소를 다시 만들까요?','예전 주소는 바로 막히고 새 주소를 만들어요. 이미 들어온 휴대폰은 그대로 봐요. 이 그룹이 같이 들어간 다른 링크도 막혀요.','다시 만들기')+base[k:]
    s2=re.sub(r'<title>(.*?)</title>',lambda m:f'<title>{m.group(1)} · 주소 다시 만들기 확인</title>',s2,count=1)
    n2='GroupResetLayer'+t+'.dc.html'; open(n2,'w').write(s2)
    sb=b['GroupDetail'+t+'.dc.html']
    for n,title in ((n1,'링크 카드'),(n2,'주소 다시 만들기 확인')):
        if n not in b:
            x=max(v['x'] for v in b.values() if v['y']==sb['y'])+470
            d['order'].append(n); b[n]=dict(sb,x=x,title=sb['title']+' · '+title)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
