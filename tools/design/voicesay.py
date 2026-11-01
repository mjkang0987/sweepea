# 음성 한마디(108, 사용자 2026-11-01: 받아 적기는 내부 Cloudflare, 최대 10초, 유료만): CommentSheet에서
# 시트 아래 입력 줄에 마이크 → 녹음 중(남은 초·막대·다 말했어요) → 받아 적는 중 → 받아 적은 글자 확인(고치기·들어 보기·다시 말하기·보내기).
# 목록의 음성 한마디는 글자 + 재생 버튼. 유료가 아닌 가족방은 마이크가 없음(지금 CommentSheet 그대로). 다시 돌려도 같게
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
MIC='<svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3" fill="none" stroke="currentColor" stroke-width="2"></rect><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path></svg>'
PLAY='<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z" fill="currentColor"></path></svg>'
BIG='min-height: 56px; box-sizing: border-box; border: 0; border-radius: 10px; font-family: inherit; font-size: 19px; line-height: 26px; font-weight: 700;'
QUIET=BIG+' padding: 0 16px; background: var(--fill); color: var(--label); display: flex; align-items: center; justify-content: center; gap: 6px;'
FIELD='flex: 1; min-width: 0; min-height: 56px; height: 56px; box-sizing: border-box; padding: 0 16px; border: 1.5px solid var(--field-border); border-radius: 10px; background: var(--bg); color: var(--label); font-family: inherit; font-size: 19px; line-height: 26px;'
SEND=f'<button type="submit" style="flex: none; {BIG} padding: 0 18px; background: var(--pea); color: var(--on-pea);">보내기</button>'
FOOT='display: flex; flex-direction: column; gap: 10px; padding: 12px 20px 34px;'
def foot():
    # 1) 말하기 전: 입력 줄 왼쪽에 마이크(유료 가족방만)
    idle=(f'<sc-if value="{{{{sIdle}}}}" hint-placeholder-val="{{{{true}}}}"><form style="display: flex; gap: 8px; padding: 12px 20px 34px;">'
          f'<button type="button" aria-label="말로 한마디(10초)" style="flex: none; width: 56px; height: 56px; padding: 0; border: 0; border-radius: 50%; background: var(--pea-tint); color: var(--pea-ink); display: flex; align-items: center; justify-content: center;">{MIC}</button>'
          '<label for="cs-msg" style="position: absolute; width: 1px; height: 1px; overflow: hidden;">하린이에게 한마디</label>'
          f'<input id="cs-msg" type="text" autocomplete="off" placeholder="글로 쓰기" style="{FIELD}">{SEND}</form></sc-if>')
    # 2) 녹음 중: 남은 초(글자) + 막대(meter), 10초에 저절로 멈춤
    rec=(f'<sc-if value="{{{{sRec}}}}" hint-placeholder-val="{{{{false}}}}"><div role="group" aria-label="말로 한마디" style="{FOOT}">'
         '<p role="status" style="margin: 0; display: flex; align-items: center; gap: 8px; font-size: 19px; line-height: 26px; font-weight: 700;">'
         '<span aria-hidden="true" style="width: 12px; height: 12px; border-radius: 50%; background: var(--danger);"></span>듣고 있어요'
         '<span style="margin-left: auto; color: var(--label-2); font-weight: 600;">7초 남았어요</span></p>'
         '<span aria-hidden="true" style="height: 8px; border-radius: 999px; background: var(--fill); overflow: hidden;"><span style="display: block; width: 30%; height: 100%; background: var(--pea);"></span></span>'
         f'<button type="button" style="{BIG} background: var(--pea); color: var(--on-pea);">다 말했어요</button></div></sc-if>')
    # 3) 받아 적는 중
    wait=(f'<sc-if value="{{{{sWait}}}}" hint-placeholder-val="{{{{false}}}}"><div style="{FOOT}">'
          '<p role="status" style="margin: 0; min-height: 56px; display: flex; align-items: center; justify-content: center; font-size: 19px; line-height: 26px; font-weight: 600; color: var(--label-2);">글자로 바꾸는 중이에요…</p></div></sc-if>')
    # 4) 받아 적은 글자 확인: 고칠 수 있는 입력칸, 들어 보기·다시 말하기, 보내기
    done=(f'<sc-if value="{{{{sDone}}}}" hint-placeholder-val="{{{{false}}}}"><form style="{FOOT}">'
          '<label for="cs-voice" style="font-size: 15px; line-height: 20px; color: var(--label-2);">이렇게 받아 적었어요. 틀린 곳은 고쳐 주세요</label>'
          # 여러 줄 칸: 10초 말이 한눈에 다 보이게(한 줄 칸은 잘려서 끝까지 확인하기 어려움)
          '<textarea id="cs-voice" rows="2" maxlength="200" style="box-sizing: border-box; width: 100%; padding: 12px 16px; border: 1.5px solid var(--field-border); border-radius: 10px; background: var(--bg); color: var(--label); font-family: inherit; font-size: 19px; line-height: 27px; word-break: keep-all; resize: none;">하린아 할머니가 많이 사랑해 감기 조심하고</textarea>'
          f'<div style="display: flex; gap: 8px;"><button type="button" aria-label="내 목소리 들어 보기, 4초" style="flex: 1; {QUIET}">{PLAY}들어 보기</button>'
          f'<button type="button" style="flex: 1; {QUIET}">{MIC}다시 말하기</button></div>'
          f'<button type="submit" style="{BIG} background: var(--pea); color: var(--on-pea);">보내기</button></form></sc-if>')
    return idle+rec+wait+done
def make(t):
    s=open(f'CommentSheet{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>음성 한마디</title>',s,count=1)
    # 시트 아래 입력 폼을 단계별 아래 칸으로
    i=s.rindex('<form style="display: flex; gap: 8px; padding: 12px 20px 34px;')
    j=s.index('</form>',i)+len('</form>')
    s=s[:i]+foot()+s[j:]
    # 목록 첫 한마디는 음성: 글자 아래 재생(엄빠·가족 모두 들음), 지우기 확인은 닫음
    s=s.replace('<details open style="flex: none;">','<details style="flex: none;">',1)
    s=re.sub(r'<form style="display: flex; align-items: center; gap: 8px; margin-top: 6px;.*?</form>','',s,count=1,flags=re.S)
    first='>아이고 우리 하린이 많이 컸네</p>'
    s=s.replace(first,first+f'<button type="button" aria-label="외할아버지 목소리 듣기, 4초" style="align-self: flex-start; margin-top: 6px; min-height: 44px; padding: 0 16px 0 12px; border: 0; border-radius: 22px; background: var(--pea-tint); color: var(--pea-ink); font-family: inherit; font-size: 17px; font-weight: 700; display: flex; align-items: center; gap: 6px;">{PLAY}목소리 0:04</button>',1)
    # 단계 고르기
    s=re.sub(r"data-props='\{\"theme\"",'data-props=\'{"step":{"editor":"enum","options":["말하기 전","녹음 중","받아 적는 중","글자 확인"],"default":"말하기 전"},"theme"',s,count=1)
    s=s.replace("return { theme:","const st = this.props.step ?? '말하기 전';\nreturn { sIdle: st === '말하기 전', sRec: st === '녹음 중', sWait: st === '받아 적는 중', sDone: st === '글자 확인', theme:",1)
    open(f'VoiceSay{t}.dc.html','w').write(s)
d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    make(t)
    ref=B[f'CommentSheet{t}.dc.html']; n=f'VoiceSay{t}.dc.html'
    if n not in d['order']: d['order'].append(n)
    x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
    B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · 앱 · 음성 한마디(앱에서만, 웹 없음) — 마이크 → 녹음 10초 → 받아 적기 → 글자 확인, 목록 재생')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
