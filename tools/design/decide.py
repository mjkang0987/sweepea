# 웹 UX 점검 남은 것 셋 — 사용자 결정용 시안(2026-11-07). 라이트만(고른 뒤 다크·실제 보드로)
# 1 한마디가 넘겨 보기에 안 보임(DecideSay-Now·A·B) 2 승인 대기 안내가 김(DecideWait-*) 3 설정 › 가족 보내는 방법 셋(DecideSend-*)
import os,re,json
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','canvas','project'))
def rd(n): return open(n).read()
def wr(n,s,title):
    s=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',s,count=1); open(n,'w').write(s)
def one(s,a,b):
    assert s.count(a)==1,(a[:60],s.count(a)); return s.replace(a,b)
P='font-family: inherit;'
# ── 1 한마디 ──
g=rd('GrandHome-Light.dc.html')
g=re.sub(r'\s*<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0;">.*?</div>','',g,count=1,flags=re.S)  # 내 캐릭터·글자 크기(넘겨 보기 맨 아래라 이 높이엔 안 보임)
now=one(g,'"default":"없음"}','"default":"한마디 보냄"}')
wr('DecideSay-Now.dc.html',now,'결정 1 · 지금: 보내도 안 보임')
def row(i,who,txt,top):
    return (f'<li style="display: flex; gap: 10px; padding: 10px 0;{top}"><span aria-hidden="true" style="flex: none; width: 36px; height: 36px; border-radius: 999px; background: var(--pea-tint); color: var(--pea-deep); display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700;">{i}</span>'
            f'<span style="font-size: 19px; line-height: 26px;"><strong>{who}</strong> {txt}</span></li>')
said=('\n    <section aria-labelledby="said" style="display: flex; flex-direction: column;"><h3 id="said" style="position: absolute; width: 1px; height: 1px; overflow: hidden;">남긴 한마디</h3>'
      '<ul style="list-style: none; margin: 0; padding: 0;">'+row('외','외할머니','아이고 우리 하린이 많이 컸네','')+row('이','이모','너무 귀엽다','border-top: 1px solid var(--separator);')+'</ul>'
      '<a href="PhotoView-Light.dc.html" style="min-height: 48px; display: flex; align-items: center; color: var(--pea-ink); text-decoration: none; font-size: 19px; font-weight: 600;">한마디 3개 모두 보기 ›</a></section>')
a=one(g,'</form>\n  </section>','</form>'+said+'\n  </section>')
a=one(a,'width: 390px; height: 844px;','width: 390px; height: 1010px;').replace('"height":844}','"height":1010}')  # 남긴 말까지 보이게 길게
wr('DecideSay-A.dc.html',a,'결정 1 · A: 카드 아래 최근 한마디 2개')
chip=('<a href="PhotoView-Light.dc.html" style="margin-left: auto; min-height: 44px; padding: 0 14px; display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; background: var(--fill); color: var(--label); text-decoration: none; font-size: 17px; font-weight: 700;">'
      '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z" fill="none" style="stroke: currentColor" stroke-width="1.8" stroke-linejoin="round"></path></svg>한마디 3</a>')
b=one(g,'10월 21일</span>\n','10월 21일</span>'+chip+'\n')
b=one(b,'보냈어요. 가족 모두 볼 수 있어요.','보냈어요. 사진 아래 \'한마디\'를 누르면 보여요.')
b=one(b,'"default":"없음"}','"default":"한마디 보냄"}')
wr('DecideSay-B.dc.html',b,'결정 1 · B: 카드에 한마디 수만')
# ── 2 승인 대기 ──
w=rd('GrandPending-Light.dc.html')
w=re.sub(r'\s*<section aria-labelledby="got-h".*?</section>','',w,count=1,flags=re.S)  # 받은 사진 없는 경우(글이 가장 긴 경우)
BOX='<p style="margin: 0; font-size: 21px; line-height: 30px;">그동안 받은 사진은 여기서 볼 수 있어요. 3일 안에 확인하지 않으면 다시 받아야 해요.</p>'
LONG='그때 사진을 볼 수 있어요. 확인돼도 알림은 가지 않아요. 엄마아빠에게 전화로 확인해 달라고 말씀하고, 확인되면 아래 \'다시 확인하기\'를 눌러 주세요. 3일 안에 확인이 없으면 엄마아빠에게 주소를 다시 받아야 해요.'
wr('DecideWait-Now.dc.html',one(w,BOX,f'<p style="margin: 0; font-size: 21px; line-height: 30px;">{LONG}</p>'),'결정 2 · 지금: 안내 9줄')
wr('DecideWait-A.dc.html',one(w,BOX,'<p style="margin: 4px 0 0; font-size: 21px; line-height: 30px;">엄마아빠에게 전화로 확인해 달라고 하세요. 알림은 따로 가지 않아요.</p>'
   '<p style="margin: 8px 0 0; font-size: 17px; line-height: 24px;">3일이 지나면 주소를 다시 받아야 해요.</p>'),'결정 2 · A: 두 줄 + 작은 글')
steps=''.join(f'<li style="display: flex; gap: 12px; align-items: flex-start;"><span aria-hidden="true" style="flex: none; width: 34px; height: 34px; margin-top: -1px; border-radius: 999px; background: var(--pea); color: var(--on-pea); display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700;">{i}</span><span>{t}</span></li>'
              for i,t in [(1,'엄마아빠에게 전화로 확인해 달라고 하세요'),(2,'확인되면 아래 \'다시 확인하기\'를 누르세요'),(3,'3일이 지나면 주소를 다시 받아야 해요')])
wr('DecideWait-B.dc.html',one(w,BOX,f'<ol style="margin: 12px 0 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 12px; font-size: 21px; line-height: 30px;">{steps}</ol>'),'결정 2 · B: 순서 1·2·3')
# ── 3 보내는 방법 ──
f=rd('FamilyCoParent-Light.dc.html')
f=one(f,'"default":"함께 관리 중"}','"default":"초대 전"}').replace("this.props.state ?? '함께 관리 중'","this.props.state ?? '초대 전'")
wr('DecideSend-Now.dc.html',f,'결정 3 · 지금: 보내는 곳 셋')
CH='<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" style="flex: none;"><path d="M9 5l7 7-7 7" fill="none" style="stroke: var(--label-2)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
def item(href,t,sub,top=''):
    return (f'<li><a href="{href}" style="display: flex; align-items: center; gap: 12px; min-height: 64px; padding: 8px 16px;{top} color: var(--label); text-decoration: none;">'
            f'<span style="flex: 1; display: flex; flex-direction: column;"><span style="font-size: 17px; line-height: 22px; font-weight: 600;">{t}</span><span style="font-size: 13px; line-height: 18px; color: var(--label-2);">{sub}</span></span>{CH}</a></li>')
SEP=' border-top: 1px solid var(--separator);'
send=('<section aria-labelledby="f-send"><h2 id="f-send" style="margin: 0 0 8px 16px; font-size: 13px; line-height: 18px; font-weight: 600; color: var(--label-2);">가족에게 보내기</h2>'
      '<ul style="list-style: none; margin: 0; padding: 0; border-radius: 16px; overflow: hidden; background: var(--surface);">'
      +item('GroupLinkCard-Light.dc.html','처음 오시는 가족','외가·친가 주소를 카톡이나 문자로 보내요')
      +item('SendSetup-Light.dc.html','이미 들어온 가족 휴대폰에','홈 화면에 스위피 두는 문자 · 처음 한 번만',SEP)
      +item('JoinParent-Light.dc.html','아빠','같이 올리고 승인하는 계정 · 초대 링크',SEP)+'</ul></section>')
A=re.sub(r'<sc-if value="\{\{isInvite\}\}".*?</sc-if>','',f,count=1,flags=re.S)
A=re.sub(r'\s*<a href="SendSetup-Light\.dc\.html".*?</a>','\n    '+send,A,count=1,flags=re.S)
wr('DecideSend-A.dc.html',A,'결정 3 · A: 보내기 한 묶음')
B=re.sub(r'<sc-if value="\{\{isInvite\}\}".*?</sc-if>','',f,count=1,flags=re.S)
B=re.sub(r'<a href="SendSetup-Light\.dc\.html".*?</a>',
  '<a href="DecideSend-B2.dc.html" style="min-height: 52px; border-radius: 12px; background: var(--pea); color: var(--on-pea); display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 17px; font-weight: 600;">가족에게 보내기</a>',B,count=1,flags=re.S)
wr('DecideSend-B.dc.html',B,'결정 3 · B: 버튼 하나')
# B 다음 화면: 누구에게(네이티브 라디오)
opts=[('first','처음 오시는 가족','외가·친가 주소를 카톡이나 문자로',True),('phone','이미 들어온 가족 휴대폰에','홈 화면에 스위피 두는 문자 · 처음 한 번만',False),('dad','아빠','같이 올리고 승인하는 계정',False)]
radios=''.join(f'<li style="{"" if i==0 else "border-top: 1px solid var(--separator);"}"><label style="display: flex; align-items: center; gap: 12px; min-height: 64px; padding: 8px 16px;"><input type="radio" name="to" value="{v}"{" checked" if c else ""} style="flex: none; width: 22px; height: 22px; margin: 0; accent-color: var(--pea);"><span style="display: flex; flex-direction: column;"><span style="font-size: 17px; line-height: 22px; font-weight: 600;">{t}</span><span style="font-size: 13px; line-height: 18px; color: var(--label-2);">{s}</span></span></label></li>' for i,(v,t,s,c) in enumerate(opts))
m=re.search(r'<main .*?</main>',f,re.S).group(0)
head=re.search(r'<div style="display: grid; grid-template-columns: repeat\(3.*?</div>',m,re.S).group(0).replace('Settings-Light.dc.html','DecideSend-B.dc.html').replace('>설정</a>','>가족</a>').replace('>가족</h1>','>보내기</h1>')
body=(f'<main style="flex: 1; min-height: 0; padding: 20px 20px 0; display: flex; flex-direction: column; gap: 24px; overflow: hidden;">{head}'
      '<form style="display: flex; flex-direction: column; gap: 16px;"><fieldset style="margin: 0; padding: 0; border: 0;"><legend style="padding: 0; margin: 0 0 12px; font-size: 22px; line-height: 28px; font-weight: 700;">누구에게 보낼까요?</legend>'
      f'<ul style="list-style: none; margin: 0; padding: 0; border-radius: 16px; overflow: hidden; background: var(--surface);">{radios}</ul></fieldset>'
      '<button type="submit" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--pea); color: var(--on-pea); '+P+' font-size: 17px; font-weight: 600;">다음</button></form></main>')
B2=f.replace(m,body)
wr('DecideSend-B2.dc.html',B2,'결정 3 · B 다음: 누구에게')
# ── 캔버스 자리·제목·메모 ──
c=json.load(open('canvas.json')); Y0=30100
rows=[('t-dsay','결정 1 · 조부모 한마디가 넘겨 보기에 안 보임',['DecideSay-Now','DecideSay-A','DecideSay-B'],
       "지금: 넘겨 보기에서 한마디를 보내면 '보냈어요' 토스트만 뜨고, 남긴 말은 사진을 눌러 크게 봐야 보여요.\n\nA (추천): 카드 아래 최근 한마디 2개 + '모두 보기'. 할머니가 쓴 말이 바로 보이고 다른 가족 말도 읽혀요. 가운데 카드가 될 때만 한마디를 받아 와요(작은 API 하나, DB 변경 없음).\n\nB: 카드에 '한마디 3' 알약만. 누르면 크게 보기. 새로 받아 올 것 없이 지금 있는 숫자로 돼요(가장 적은 변경). 대신 말 자체는 여전히 한 번 더 눌러야 보여요."),
      ('t-dwait','결정 2 · 승인 기다리는 화면 안내가 큰 글자로 9줄',['DecideWait-Now','DecideWait-A','DecideWait-B'],
       "지금: 다섯 문장이 한 덩어리(받은 사진이 없을 때, 큰 글자로 9줄).\n\nA (추천): 할 일 한 문장 + 알림 안 감 + 작은 글로 3일. 꼭 알아야 할 '전화로 부탁'과 '알림 안 감'은 남기고 나머지는 버튼이 대신 말해요.\n\nB: 1·2·3 순서. 따라 하기는 가장 쉽지만 화면을 더 차지해요(받은 사진이 있으면 사진이 더 아래로)."),
      ('t-dsend','결정 3 · 설정 › 가족에 보내는 곳이 셋(아빠 초대·문자로 공유·링크 만들기)',['DecideSend-Now','DecideSend-A','DecideSend-B','DecideSend-B2'],
       "지금: '아빠 초대하기'(맨 위), '문자로 공유하기'(가운데 카드), 그룹마다 '링크 만들기'(아래)가 흩어져 있어서 누구에게 무엇을 보내는지 헷갈려요.\n\nA (추천): '가족에게 보내기' 한 묶음에 받는 사람으로 세 줄 — 처음 오시는 가족(그룹 링크) · 이미 들어온 가족 휴대폰에(문자) · 아빠(함께 관리). 누르면 지금 있는 화면으로 가요. 그룹 줄의 '링크 만들기'는 그룹 자세히로.\n\nB: 버튼 하나 '가족에게 보내기' → 다음 화면에서 누구에게(라디오 셋) 고르고 다음. 가장 단순해 보이지만 한 번 더 눌러야 해요.")]
for r,(nid,title,names,memo) in enumerate(rows):
    y=Y0+r*1400
    c['notes'][nid]={'kind':'title1','x':0,'y':y,'maxW':2300,'text':title}
    for i,n in enumerate(names):
        k=n+'.dc.html'; c['boards'][k]={'x':i*470,'y':y+240,'w':390,'h':1010 if n=='DecideSay-A' else 844,'title':title.split(' · ')[0]+' · '+rd(k).split('<title>')[1].split('</title>')[0].split(' · ',1)[1]}
        if k not in c['order']: c['order'].append(k)
    c['notes'][nid+'-m']={'x':len(names)*470+40,'y':y+240,'w':520,'text':memo,'size':'m','fill':'yellow' if False else 'teal'}
json.dump(c,open('canvas.json','w'),ensure_ascii=False,indent=2)
print('ok')
