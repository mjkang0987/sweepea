# 엄마아빠 공동 관리자(100, 사용자 2026-10-29 "권한은 공동으로", 엄빠 최대 둘·서로 내보내기·한 명 탈퇴는 나만 나가기)
# ① FamilyCoParent: 설정 › 가족 맨 위 '엄마아빠' 줄(state: 초대 전 / 링크 만듦 / 함께 관리 중 / 내보내기 확인). 링크 카드는 GroupLinkCard, 레이어는 FamilyRevokeLayer 모양
# ② JoinParent: 초대 받은 화면 /join/<코드>(state: 초대 / 이미 다른 앨범 / 기간 지남). 로그인 버튼은 ParentLogin
# ③ AccountLeave: 엄빠가 둘일 때 계정 › 탈퇴 레이어는 '이 앨범에서 나가기'(AccountDelete 모양). 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
KONGI=re.search(r'src="(data:image/svg\+xml;base64,[^"]*)"',open('Landing-Light.dc.html').read()).group(1)
H2='margin: 0 0 8px 16px; font-size: 13px; line-height: 18px; font-weight: 600; color: var(--label-2);'
def avatar(ch): return f'<span aria-hidden="true" style="flex: none; width: 44px; height: 44px; border-radius: 999px; background: var(--pea-tint); color: var(--pea-deep); display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700;">{ch}</span>'
def row(ch,name,sub,right='',top=False):
    bt=' border-top: 1px solid var(--separator);' if top else ''
    return (f'<li style="display: flex; align-items: center; gap: 12px; min-height: 64px; padding: 8px 8px 8px 16px;{bt}">{avatar(ch)}'
            f'<span style="flex: 1; display: flex; flex-direction: column;"><span style="font-size: 17px; line-height: 22px; font-weight: 600;">{name}</span><span style="font-size: 13px; line-height: 18px; color: var(--label-2);">{sub}</span></span>{right}</li>')
OUT_BTN='<button type="button" style="min-height: 44px; padding: 0 12px; border: 0; border-radius: 10px; background: transparent; color: var(--danger); font-family: inherit; font-size: 15px; font-weight: 600;">내보내기</button>'
def section(state):
    me=row('엄','엄마 (나)','카카오로 로그인')
    together=row('아','아빠','네이버로 로그인 · 10월 29일부터 함께',OUT_BTN,True)
    invite=('<li style="border-top: 1px solid var(--separator); padding: 12px 16px 16px; display: flex; flex-direction: column; gap: 10px;">'
            '<p style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">아빠도 자기 계정으로 사진 올리기·가족 승인·설정을 같이 할 수 있어요.</p>'
            '<button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--pea); color: var(--on-pea); font-family: inherit; font-size: 17px; font-weight: 600;">아빠 초대하기</button></li>')
    card=('<li style="border-top: 1px solid var(--separator); padding: 12px 16px 16px; display: flex; flex-direction: column; gap: 10px;">'
          '<strong style="font-size: 17px; line-height: 22px;">아빠에게 보낼 링크를 만들었어요</strong>'
          '<label for="cp-u" style="font-size: 15px; font-weight: 700;">주소</label>'
          '<input id="cp-u" type="url" readonly value="https://sweepea.co.kr/join/Pq8wZ3nT" style="box-sizing: border-box; width: 100%; height: 52px; padding: 0 16px; border: 1.5px solid var(--label-2); border-radius: 12px; background: var(--bg); color: var(--label); font-family: inherit; font-size: 17px;">'
          '<a href="#" style="min-height: 52px; border-radius: 12px; background: var(--pea); color: var(--on-pea); display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 17px; font-weight: 600;">카톡·문자로 보내기</a>'
          '<button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">주소 복사</button>'
          '<p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">한 번만 쓸 수 있고 3일 뒤에 사라져요. 받은 사람이 로그인하면 바로 함께 관리해요.</p></li>')
    return (f'<section aria-labelledby="f-par">\n      <h2 style="{H2}"><span id="f-par">엄마아빠</span> · 함께 관리</h2>\n'
            '      <ul style="list-style: none; margin: 0; padding: 0; border-radius: 16px; overflow: hidden; background: var(--surface);">'
            + me
            + '<sc-if value="{{isInvite}}" hint-placeholder-val="{{false}}">'+invite+'</sc-if>'
            + '<sc-if value="{{isLink}}" hint-placeholder-val="{{false}}">'+card+'</sc-if>'
            + '<sc-if value="{{isTogether}}" hint-placeholder-val="{{true}}">'+together+'</sc-if>'
            + '</ul>\n    </section>\n    ')
LAYER=('<sc-if value="{{isRemove}}" hint-placeholder-val="{{false}}">'
       '<div class="sp-layer-scrim" aria-hidden="true" style="position: absolute; inset: 0; z-index: 50; background: rgba(0,0,0,0.45);"></div>'
       '<dialog class="sp-layer-box" open aria-labelledby="cp-t" aria-describedby="cp-d" style="position: absolute; z-index: 51; left: 20px; right: 20px; top: 50%; transform: translateY(-50%); margin: 0; width: auto; box-sizing: border-box; padding: 24px 20px 20px; border: 0; border-radius: 22px; background: var(--surface); color: var(--label); display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; word-break: keep-all;">'
       '<h2 id="cp-t" style="margin: 0; font-size: 20px; line-height: 26px; font-weight: 700;">아빠를 함께 관리에서 내보낼까요?</h2>'
       '<p id="cp-d" style="margin: 0; font-size: 15px; line-height: 21px; color: var(--label-2);">아빠 계정으로는 이 앨범을 더 볼 수 없어요. 아빠가 올린 사진과 남긴 한마디는 그대로 있어요. 다시 함께하려면 새로 초대해 주세요.</p>'
       '<div style="align-self: stretch; display: flex; flex-direction: column; gap: 8px; margin-top: 4px;">'
       '<button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--danger); color: var(--bg); font-family: inherit; font-size: 17px; font-weight: 600;">내보내기</button>'
       '<button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">취소</button>'
       '</div></dialog></sc-if>\n')
def props(th,name,opts,default):
    return '{"theme":{"editor":"enum","options":["system","light","dark"],"default":"%s"},"%s":{"editor":"enum","options":%s,"default":"%s"},"$preview":{"width":390,"height":844}}'%(th,name,json.dumps(opts,ensure_ascii=False),default)

def family(t,default,title):
    s=open(f'Family{t}.dc.html').read()
    th='light' if t else 'dark'
    # 위험 색(--danger)·레이어 스타일이 있는 FamilyRevokeLayer의 helmet으로
    r=open(f'FamilyRevokeLayer{t}.dc.html').read()
    s=s[:s.index('<helmet>')]+r[r.index('<helmet>'):r.index('</helmet>')]+s[s.index('</helmet>'):]
    s=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',s,count=1)
    # 새로 들어온 기기 칸은 빼서 자리 확보, 맨 위(문자로 공유하기 앞)에 엄마아빠 줄
    s=re.sub(r'\s*<section aria-labelledby="f-dev">.*?</section>','',s,count=1,flags=re.S)
    i=s.index('<a href="SendSetup'); s=s[:i]+section(default)+s[i:]
    j=s.rindex('</div>\n</x-dc>'); s=s[:j]+LAYER+s[j:]
    s=re.sub(r"<script type=\"text/x-dc\" data-dc-script data-props='[^']*'>.*?</script>",
             "<script type=\"text/x-dc\" data-dc-script data-props='"+props(th,'state',['초대 전','링크 만듦','함께 관리 중','내보내기 확인'],default)+"'>\nclass Component extends DCLogic {\nrenderVals() {\nconst s = this.props.state ?? '"+default+"';\nreturn { theme: this.props.theme ?? '"+th+"', isInvite: s === '초대 전', isLink: s === '링크 만듦', isTogether: s === '함께 관리 중' || s === '내보내기 확인', isRemove: s === '내보내기 확인' };\n}\n}\n</script>",s,count=1,flags=re.S)
    assert 'isRemove' in s
    return s

def join(t):
    s=open('ParentLogin.dc.html').read(); th='light' if t else 'dark'
    s=re.sub(r'<title>.*?</title>','<title>함께 관리 초대</title>',s,count=1)
    s=s.replace('src="/_blob/18a8457a415dd2214e041f90295e4f10" alt=""',f'src="{KONGI}" alt=""')
    a=s.index('<h1 '); b=s.index('</p>',a)+4
    head=('<sc-if value="{{isInvite}}" hint-placeholder-val="{{true}}"><h1 style="margin: 0; font-size: 28px; line-height: 36px; font-weight: 800; letter-spacing: -0.02em;">하린이 앨범을<br>함께 관리해요</h1>'
          '<p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">엄마가 초대했어요. 로그인하면 사진 올리기·가족 승인·설정을 같이 할 수 있어요.</p></sc-if>'
          '<sc-if value="{{isOther}}" hint-placeholder-val="{{false}}"><h1 style="margin: 0; font-size: 28px; line-height: 36px; font-weight: 800;">이미 다른 앨범을<br>관리하고 있어요</h1>'
          '<p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">한 계정은 앨범 하나만 관리할 수 있어요. 다른 계정으로 로그인하거나, 지금 앨범에서 나간 뒤 다시 열어 주세요.</p></sc-if>'
          '<sc-if value="{{isOld}}" hint-placeholder-val="{{false}}"><h1 style="margin: 0; font-size: 28px; line-height: 36px; font-weight: 800;">초대 링크가<br>지났어요</h1>'
          '<p style="margin: 0; font-size: 17px; line-height: 24px; color: var(--label-2);">이미 썼거나 3일이 지났어요. 초대한 사람에게 새 링크를 부탁해 주세요.</p></sc-if>')
    s=s[:a]+head+s[b:]
    # 로그인 버튼 위에 엄마·아빠 고르기(가족 화면에 '오늘 아빠가 올렸어요'로 보임)
    k=s.index('<button type="button"',s.index('<div style="display: flex; flex-direction: column; gap: 10px; padding-bottom: 28px;">'))
    pick=('<fieldset style="margin: 0 0 6px; padding: 0; border: 0; min-width: 0;"><legend style="margin: 0 0 8px; font-size: 15px; font-weight: 700;">나는</legend>'
          '<div style="display: flex; gap: 2px; padding: 2px; background: var(--fill); border-radius: 10px;">'
          '<label style="flex: 1; min-height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 17px; font-weight: 500;"><input type="radio" name="role" value="mom" style="position: absolute; opacity: 0; width: 1px; height: 1px;">엄마</label>'
          '<label style="flex: 1; min-height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 8px; background: var(--seg); box-shadow: 0 1px 2px rgba(0,0,0,0.12); font-size: 17px; font-weight: 600;"><input type="radio" name="role" value="dad" checked style="position: absolute; opacity: 0; width: 1px; height: 1px;">아빠</label>'
          '</div></fieldset>')
    s=s[:k]+'<sc-if value="{{isInvite}}" hint-placeholder-val="{{true}}">'+pick+'</sc-if>'+s[k:]
    s=re.sub(r"<script type=\"text/x-dc\" data-dc-script data-props='[^']*'>.*?</script>",
             "<script type=\"text/x-dc\" data-dc-script data-props='"+props(th,'state',['초대','이미 다른 앨범','기간 지남'],'초대')+"'>\nclass Component extends DCLogic {\nrenderVals() {\nconst s = this.props.state ?? '초대';\nreturn { theme: this.props.theme ?? '"+th+"', isInvite: s === '초대', isOther: s === '이미 다른 앨범', isOld: s === '기간 지남' };\n}\n}\n</script>",s,count=1,flags=re.S)
    return s

def leave(t):
    s=open(f'AccountDelete{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>이 앨범에서 나가기</title>',s,count=1)
    a=s.index('<dialog open'); b=s.index('</dialog>',a)+len('</dialog>')
    d=s[a:b]
    d=re.sub(r'(<h2[^>]*>).*?(</h2>)',r'\1이 앨범에서 나갈까요?\2',d,count=1,flags=re.S)
    d=re.sub(r'(<h2[^>]*>.*?</h2>\s*<p[^>]*>).*?(</p>)',r'\1아빠가 계속 관리해요. 사진과 가족은 그대로 남고, 내 계정만 빠져요. 다시 함께하려면 아빠에게 초대를 받아 주세요.\2',d,count=1,flags=re.S)
    d=re.sub(r'\s*<label[^>]*>\s*<input type="checkbox".*?</label>','',d,count=1,flags=re.S)
    d=d.replace('>탈퇴하기<','>나가기<').replace('<button type="button" disabled style=','<button type="button" style=').replace('; opacity: 0.4;">나가기','">나가기').replace('background: var(--danger); color: #ffffff">나가기','background: var(--danger); color: var(--bg)">나가기')  # 다크(#ff6961)에서 흰 글자는 대비 부족
    return s[:a]+d+s[b:]

d=json.load(open('canvas.json')); B=d['boards']
for t in ['','-Light']:
    files={f'FamilyCoParent{t}.dc.html':(family(t,'함께 관리 중','가족 · 함께 관리'),'Family','부모 · 설정 › 가족 · 엄마아빠 함께 관리(초대 전·링크·함께·내보내기)'),
           f'FamilyCoParentInvite{t}.dc.html':(family(t,'링크 만듦','가족 · 함께 관리 초대 링크'),'Family','부모 · 설정 › 가족 · 함께 관리 초대 링크'),
           f'CoParentRemoveLayer{t}.dc.html':(family(t,'내보내기 확인','가족 · 함께 관리 내보내기'),'Family','부모 · 함께 관리 내보내기 확인'),
           f'JoinParent{t}.dc.html':(join(t),'ParentLogin','부모 · 함께 관리 초대 받음(/join, 이미 다른 앨범·기간 지남)'),
           f'AccountLeave{t}.dc.html':(leave(t),'AccountDelete','부모 · 계정 › 이 앨범에서 나가기(엄빠 둘일 때)')}
    for n,(html,base,label) in files.items():
        open(n,'w').write(html)
        ref=B.get(base+t+'.dc.html') or B[base+'.dc.html']
        if n not in d['order']: d['order'].append(n)
        x=B[n]['x'] if n in B else max(v['x'] for v in B.values() if v['y']==ref['y'])+470
        B[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · '+label)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
