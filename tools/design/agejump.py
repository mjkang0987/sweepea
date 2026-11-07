# 아이 나이별로 건너뛰기(98, 사용자 2026-10-29 "있는 월별·연별에 붙이기"): 이미 있는 모아 보기 칸 단계(1·2·3·5·월·연)의
# 마지막 '연' 단계를 아이가 하나면 나이별 카드(첫돌 ~ 지금 · 백일 ~ 첫돌 · 태어나서 ~ 백일 · 태어나기 전)로. 여러 아이·여러 집이면 연도 그대로.
# GrandList는 고치고(안내 글·카드 글자 줄·kids 속성), 나이별로 열린 GrandListAge, 부모 홈 나이별 ParentHomeAge를 새로. 라이트·다크
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
AGES=("[['첫돌 ~ 지금',42,'2026년 9월부터'],['백일 ~ 첫돌',180,'2025년 12월 – 2026년 9월'],"
      "['태어나서 ~ 백일',96,'2025년 9월 – 12월'],['태어나기 전',12,'2025년 6월 – 9월']]")
YEARS_OLD="const years = [['2026년',312,'1–10월'],['2025년',148,'9–12월']].map("
YEARS_NEW=f"const years = (this.props.kids === '여럿' ? [['2026년',312,'1–10월'],['2025년',148,'9–12월']] : {AGES}).map("
CARD_OLD='<span style="display: flex; align-items: baseline; justify-content: space-between; padding: 14px 16px 16px;"><strong style="font-size: 28px; line-height: 34px; font-weight: 800; letter-spacing: -0.4px;">{{y.title}}</strong>'
CARD_NEW='<span style="display: flex; flex-direction: column; gap: 2px; padding: 14px 16px 16px;"><strong style="font-size: 26px; line-height: 32px; font-weight: 800; letter-spacing: -0.4px;">{{y.title}}</strong>'
KIDS='"kids":{"editor":"enum","options":["하나","여럿"],"default":"하나"},'

# 크게(1·2칸)는 주마다 대표 사진만(1칸 1장, 2칸 4장까지, 하트·한마디 많은 순) + 'N장 모두 보기'(3칸으로), 3·5칸은 사진 전부(사용자 2026-10-29)
REP_DONE=[None]
def rep(s):
    s=s.replace('두 손가락으로 벌리면 크게, 오므리면 작게 · 더 오므리면 월별, 나이별로','크게 보면 주마다 대표 사진, 작게 보면 사진 전부 · 더 작게 하면 월별, 나이별로')
    s=s.replace("const lv = (this.state || {}).lv ?? start; const L = levels[lv]; const last = levels.length - 1;",
                "const lv = (this.state || {}).lv ?? start; const L = levels[lv]; const last = levels.length - 1;\nconst go = (v) => () => this.setState({ lv: v });")
    s=s.replace("\nconst go = (v) => () => this.setState({ lv: v });\nconst months","\nconst months")
    s=s.replace("const days = [['10월 21일',12],","const weeks = [['10월 넷째 주',20],['10월 셋째 주',8],['10월 첫째 주',6],['9월 넷째 주',10],['9월 셋째 주',7]];\nconst days = [['10월 21일',12],")
    s=s.replace("sections = days.map(function (d) {","const rep = L.n <= 2;\nsections = (rep ? weeks : days).map(function (d) {\nconst shown = rep ? Math.min(d[1], L.n === 1 ? 1 : 4) : d[1];")
    s=s.replace("for (let i = 0; i < d[1]; i++, k++) {","for (let i = 0; i < shown; i++, k++) {")
    s=s.replace("return { title: d[0], count: d[1], cols: cols };","return { title: d[0], count: d[1], cols: cols, rep: rep, moreLabel: d[1] + '장 모두 보기', more: go(2) };")
    anchor='            </sc-for>\n          </div>\n        </div>\n      </sc-for>'  # 섹션 grid 닫힘 뒤, 섹션 div 닫기 전
    g=s.index(anchor)+len('            </sc-for>\n          </div>\n')
    btn=('          <sc-if value="{{sec.rep}}" hint-placeholder-val="{{false}}"><button type="button" onClick="{{sec.more}}" style="margin: -8px 20px 20px; min-height: 56px; width: calc(100% - 40px); border: 0; border-radius: 999px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; line-height: 24px; font-weight: 600; cursor: pointer;">{{sec.moreLabel}}</button></sc-if>\n')
    s=s[:g]+btn+s[g:]
    assert 'const rep = L.n <= 2;' in s and 'more: go(2)' in s and s.count('const go =')==1
    REP_DONE[0]=s
def grand(t):
    n=f'GrandList{t}.dc.html'; s=open(n).read()
    if '"kids"' not in s:
        s=s.replace('더 오므리면 월별, 연별로','더 오므리면 월별, 나이별로')
        assert YEARS_OLD in s and CARD_OLD in s
        s=s.replace(YEARS_OLD,YEARS_NEW).replace(CARD_OLD,CARD_NEW)
        s=s.replace('"zoom":{',KIDS+'"zoom":{',1)
        rep(s); s=REP_DONE[0]
        open(n,'w').write(s)
    # 나이별로 열린 보드
    a=s.replace('"options":["1","2","3","5","월","연"],"default":"2"','"options":["1","2","3","5","월","연"],"default":"연"',1)
    a=re.sub(r'<title>.*?</title>','<title>모아 보기 · 나이별</title>',a,count=1)
    open(f'GrandListAge{t}.dc.html','w').write(a)

SEG_ON='background: var(--seg); box-shadow: 0 1px 2px rgba(0,0,0,0.12); font-size: 15px; font-weight: 600;'
SEG_OFF='font-size: 15px; font-weight: 500;'
def chip(label,on,href):
    st=('background: var(--pea-tint); color: var(--pea-deep); font-weight: 700;' if on else 'background: var(--fill); color: var(--label); font-weight: 500;')
    cur=' aria-current="page"' if on else ''
    return f'<a href="{href}"{cur} style="min-height: 40px; padding: 0 16px; display: flex; align-items: center; border-radius: 999px; text-decoration: none; font-size: 15px; line-height: 20px; {st}">{label}</a>'
def card(title,count,sub,ph):
    return ('<a href="#" aria-label="'+title+' 사진 '+str(count)+'장 보기" style="display: block; border-radius: 18px; overflow: hidden; background: var(--surface); color: var(--label); text-decoration: none;">'
            f'<span style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 2px; height: 132px;"><span style="grid-column: span 2; grid-row: span 2; background: var(--ph-{ph});"></span><span style="background: var(--ph-{3-ph});"></span><span style="background: var(--ph-{ph});"></span><span style="background: var(--ph-{ph});"></span><span style="background: var(--ph-{3-ph});"></span></span>'
            f'<span style="display: flex; flex-direction: column; gap: 2px; padding: 10px 14px 12px;"><strong style="font-size: 20px; line-height: 26px; font-weight: 700; letter-spacing: -0.3px;">{title}</strong><span style="font-size: 13px; line-height: 18px; color: var(--label-2);">{sub} · 사진 {count}</span></span></a>')
def parent(t):
    s=open(f'ParentHome{t}.dc.html').read()
    s=re.sub(r'<title>.*?</title>','<title>앨범 · 나이별</title>',s,count=1)
    s=s.replace('"options":["승인 요청","설치 부탁","올리는 중","올리기 실패","없음"],"default":"승인 요청"','"options":["승인 요청","설치 부탁","올리는 중","올리기 실패","없음"],"default":"없음"',1)
    # 아이 탭: 하린을 고른 상태
    s=s.replace(f'{SEG_ON}"><input type="radio" name="kid" value="all" checked',f'{SEG_OFF}"><input type="radio" name="kid" value="all"',1)
    s=s.replace(f'{SEG_OFF}"><input type="radio" name="kid" value="harin"',f'{SEG_ON}"><input type="radio" name="kid" value="harin" checked',1)
    i=s.index('</fieldset>')+len('</fieldset>'); j=s.index('</main>')
    nav=('\n    <nav aria-label="보는 방법" style="display: flex; gap: 8px;">'+chip('사진',False,'ParentHome'+t+'.dc.html')+chip('월별',False,'#')+chip('나이별',True,'ParentHomeAge'+t+'.dc.html')+'</nav>'
         '\n    <p style="margin: -4px 0 0; font-size: 13px; line-height: 18px; color: var(--label-2);">전체를 고르면 나이 대신 연도별로 보여요</p>')
    cards=''.join(card(*c) for c in [('첫돌 ~ 지금',42,'2026년 9월부터',1),('백일 ~ 첫돌',180,'2025년 12월 – 2026년 9월',2),('태어나서 ~ 백일',96,'2025년 9월 – 12월',1),('태어나기 전',12,'2025년 6월 – 9월',2)])
    s=s[:i]+nav+'\n    <div style="display: flex; flex-direction: column; gap: 12px;">'+cards+'</div>\n  '+s[j:]
    open(f'ParentHomeAge{t}.dc.html','w').write(s)

d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    grand(t); parent(t)
    for name,base,label in [('GrandListAge','GrandList','조부모 웹 · 모아 보기 · 나이별(아이 하나, 여럿이면 연도)'),('ParentHomeAge','ParentHome','부모 앱 · 앨범 · 나이별(전체면 연도별)')]:
        n=name+t+'.dc.html'; ref=b[base+t+'.dc.html']
        if n not in d['order']: d['order'].append(n)
        x=b[n]['x'] if n in b else max(v['x'] for v in b.values() if v['y']==ref['y'])+470
        b[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · '+label)
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok')
