# 운영자 화면 1단계(plan 164, 사용자 2026-11-04): 현황·가족방 목록·가족방 상세 + 방문 기록. 옆 메뉴 + 두 단(사용자 고름 B), 휴대폰은 위 메뉴 한 단
# 이름·사진·한마디 내용은 안 보임 → 가족방은 번호 앞 8자리, 그룹은 '그룹 1', 사람은 '엄빠 1'·'가족 기기 3'
import os,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))

TOK='''@font-face{font-family:"Pretendard Variable";src:url("ds/sweepea/fonts/PretendardVariable.woff2") format("woff2-variations");font-weight:45 920;font-display:swap}
body{margin:0}
.sp-t{--bg:#ffffff;--surface:#f5f5f7;--fill:#e8e8ed;--separator:#d2d2d7;--label:#1d1d1f;--label-2:#636366;--pea:#0f766e;--on-pea:#ffffff;--pea-ink:#0f766e;--pea-tint:#e7f1f0;--pea-deep:#115e59;--blossom:#c8385f;--danger:#d70015;--bar:rgba(255,255,255,0.92)}
.sp-dark{--bg:#000000;--surface:#1c1c1e;--fill:#2c2c2e;--separator:#38383a;--label:#f5f5f7;--label-2:#a1a1a6;--pea:#2dd4bf;--on-pea:#000000;--pea-ink:#2dd4bf;--pea-tint:#07221f;--pea-deep:#99f6e4;--blossom:#ff6b8b;--danger:#ff6961;--bar:rgba(22,22,24,0.92);color-scheme:dark}
@media (prefers-color-scheme: dark){.sp-system{--bg:#000000;--surface:#1c1c1e;--fill:#2c2c2e;--separator:#38383a;--label:#f5f5f7;--label-2:#a1a1a6;--pea:#2dd4bf;--on-pea:#000000;--pea-ink:#2dd4bf;--pea-tint:#07221f;--pea-deep:#99f6e4;--blossom:#ff6b8b;--danger:#ff6961;--bar:rgba(22,22,24,0.92)}}
.sp-meter{-webkit-appearance:none;appearance:none;border:0;border-radius:999px;background:var(--fill);overflow:hidden}.sp-meter::-webkit-meter-bar{background:var(--fill);border:0;border-radius:999px}.sp-meter::-webkit-meter-optimum-value,.sp-meter::-webkit-meter-suboptimum-value,.sp-meter::-webkit-meter-even-less-good-value{background:var(--pea);border-radius:999px}.sp-meter::-moz-meter-bar{background:var(--pea);border-radius:999px}
.sp-o-row:hover{background:var(--fill)}'''

FONT="font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif"
CARD='padding: 16px; border-radius: 16px; background: var(--surface); display: flex; flex-direction: column; gap: 12px; min-width: 0;'
H2='margin: 0; font-size: 17px; line-height: 22px; font-weight: 600;'
SUB='margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);'
NUM='font-size: 28px; line-height: 34px; font-weight: 700; letter-spacing: -0.4px; font-variant-numeric: tabular-nums;'

def page(title,body,theme,w,h):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
{TOK}
</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"theme":{{"editor":"enum","options":["system","light","dark"],"default":"{theme}"}},"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{ theme: this.props.theme ?? '{theme}' }}; }}
}}
</script>
</body>
</html>
'''

AC=' aria-current="page"'
def nav(cur,side):
    items=[('현황','OpsHome'),('가족방','OpsFamilies')]
    if side:
        links=''.join(f'<a href="{f}{{{{sfx}}}}.dc.html"{AC if n==cur else ""} style="display: flex; align-items: center; min-height: 44px; padding: 0 12px; border-radius: 10px; text-decoration: none; font-size: 15px; line-height: 20px; {"background: var(--pea-tint); color: var(--pea-deep); font-weight: 600;" if n==cur else "color: var(--label); font-weight: 500;"}">{n}</a>' for n,f in items)
        return f'''<nav aria-label="운영 메뉴" style="flex: none; width: 220px; box-sizing: border-box; padding: 24px 16px; border-right: 1px solid var(--separator); display: flex; flex-direction: column; gap: 4px;">
    <p style="margin: 0 0 16px 12px; font-size: 17px; line-height: 22px; font-weight: 700;">스위피 운영</p>
    {links}
  </nav>'''
    links=''.join(f'<a href="{f}{{{{sfx}}}}.dc.html"{AC if n==cur else ""} style="display: flex; align-items: center; min-height: 44px; padding: 0 12px; text-decoration: none; font-size: 15px; line-height: 20px; {"color: var(--pea-ink); font-weight: 600; box-shadow: inset 0 -2px 0 var(--pea-ink);" if n==cur else "color: var(--label-2); font-weight: 500;"}">{n}</a>' for n,f in items)
    return f'''<header style="flex: none; display: flex; align-items: center; gap: 8px; padding: 0 12px 0 20px; border-bottom: 1px solid var(--separator); background: var(--bar);"><p style="margin: 0 auto 0 0; font-size: 15px; line-height: 20px; font-weight: 700;">스위피 운영</p><nav aria-label="운영 메뉴" style="display: flex;">{links}</nav></header>'''

def shell(cur,main,side=True):
    d='row' if side else 'column'
    return f'''<div class="sp-t sp-{{{{theme}}}}" style="box-sizing: border-box; min-height: 100vh; display: flex; flex-direction: {d}; background: var(--bg); color: var(--label); {FONT}; word-break: keep-all;">
  {nav(cur,side)}
  <main style="flex: 1; min-width: 0; box-sizing: border-box; padding: {'32px 32px 48px' if side else '20px 16px 40px'}; display: flex; flex-direction: column; gap: 20px;">
{main}
  </main>
</div>'''

def head(h1,sub):
    return f'<header><h1 style="margin: 0; font-size: 34px; line-height: 41px; font-weight: 700; letter-spacing: -0.4px;">{h1}</h1><p style="margin: 4px 0 0; font-size: 15px; line-height: 20px; color: var(--label-2);">{sub}</p></header>'

def stat(label,val,note=''):
    n=f'<p style="{SUB}">{note}</p>' if note else ''
    return f'<div style="padding: 14px 16px; border-radius: 16px; background: var(--surface); min-width: 0;"><p style="{SUB}">{label}</p><p style="margin: 2px 0 0; {NUM}">{val}</p>{n}</div>'

def stats(items,cols):
    return f'<div style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: 12px;">'+''.join(stat(*i) for i in items)+'</div>'

def dates(n):
    # 보드 기준일 11월 4일에서 거꾸로 n일
    import datetime as dt
    end=dt.date(2026,11,4)
    return [f'{d.month}월 {d.day}일' for d in (end-dt.timedelta(days=n-1-i) for i in range(n))]

def bars(label,days,a,b=None,la='',lb='',unit='회'):
    # a 위(가족), b 아래(엄빠) 쌓기. 이어진 두 색은 밝기가 달라 색 없이도 구분
    # 막대마다 title(마우스 말풍선, 스크립트 없음) + 아래 접힌 '숫자로 보기' 표(휴대폰·키보드·화면 읽기)
    ds=dates(len(a)); mx=max((x+(b[i] if b else 0)) for i,x in enumerate(a))
    cols=''
    for i,x in enumerate(a):
        y=b[i] if b else 0
        tip=f'{ds[i]} · {la} {x}{unit} · {lb} {y}{unit}' if b else f'{ds[i]} · {x}{unit}'
        cols+=f'<div title="{tip}" style="flex: 1; display: flex; flex-direction: column-reverse; gap: 2px; height: 100%;"><span style="height: {y/mx*100:.1f}%; border-radius: 3px; background: var(--label-2);"></span><span style="height: {x/mx*100:.1f}%; border-radius: 3px; background: var(--pea);"></span></div>'
    legend=''
    if b: legend=f'<p style="{SUB} display: flex; gap: 16px;"><span style="display: inline-flex; align-items: center; gap: 6px;"><span aria-hidden="true" style="width: 10px; height: 10px; border-radius: 3px; background: var(--pea);"></span>{la}</span><span style="display: inline-flex; align-items: center; gap: 6px;"><span aria-hidden="true" style="width: 10px; height: 10px; border-radius: 3px; background: var(--label-2);"></span>{lb}</span></p>'
    hd=['날짜']+([la,lb] if b else ['수'])
    TD='padding: 0 8px; height: 36px; text-align: right; font-variant-numeric: tabular-nums;'
    th=''.join(f'<th scope="col" style="{TD} text-align: {"left" if i==0 else "right"}; font-size: 13px; font-weight: 500; color: var(--label-2);">{h}</th>' for i,h in enumerate(hd))
    rows=''.join(f'<tr style="border-top: 1px solid var(--separator);"><th scope="row" style="{TD} text-align: left; font-weight: 400;">{ds[i]}</th><td style="{TD}">{x}{unit}</td>'+(f'<td style="{TD}">{b[i]}{unit}</td>' if b else '')+'</tr>' for i,x in reversed(list(enumerate(a))))
    table=f'<details style="font-size: 15px; line-height: 20px;"><summary style="display: inline-flex; align-items: center; min-height: 44px; color: var(--pea-ink); cursor: pointer;">숫자로 보기</summary><table style="width: 100%; border-collapse: collapse;"><caption style="position: absolute; width: 1px; height: 1px; overflow: hidden;">{label}, 날짜별 숫자</caption><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></details>'
    return f'''<figure style="margin: 0; display: flex; flex-direction: column; gap: 8px;"><div role="img" aria-label="{label}" style="display: flex; align-items: flex-end; gap: 4px; height: 120px;">{cols}</div><figcaption style="{SUB} display: flex; justify-content: space-between;"><span>{days[0]}</span><span>{days[1]}</span></figcaption>{legend}{table}</figure>'''

def card(title,inner,sub=''):
    s=f'<p style="{SUB}">{sub}</p>' if sub else ''
    return f'<section style="{CARD}"><div><h2 style="{H2}">{title}</h2>{s}</div>{inner}</section>'

def rowlink(text,meta,href):
    return f'<li><a class="sp-o-row" href="{href}" style="display: flex; align-items: center; gap: 12px; min-height: 52px; padding: 6px 8px; border-radius: 10px; color: var(--label); text-decoration: none;"><span style="flex: 1; min-width: 0;"><span style="display: block; font-size: 15px; line-height: 20px; font-weight: 500;">{text}</span><span style="display: block; font-size: 13px; line-height: 18px; color: var(--label-2);">{meta}</span></span><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" style="flex: none;"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></path></svg></a></li>'

def kv(rows):
    return '<dl style="margin: 0; display: grid; grid-template-columns: 1fr auto; gap: 8px 16px; font-size: 15px; line-height: 20px;">'+''.join(f'<dt style="color: var(--label-2);">{k}</dt><dd style="margin: 0; text-align: right; font-weight: 600; font-variant-numeric: tabular-nums;">{v}</dd>' for k,v in rows)+'</dl>'

def funnel(steps):
    mx=steps[0][1]
    return '<ol style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 10px;">'+''.join(f'<li style="display: grid; grid-template-columns: 9.5rem 1fr 3rem; align-items: center; gap: 12px; font-size: 15px; line-height: 20px;"><span>{n}</span><span aria-hidden="true" style="height: 12px; border-radius: 999px; background: var(--fill);"><span style="display: block; width: {v/mx*100:.0f}%; height: 100%; border-radius: 999px; background: var(--pea);"></span></span><span style="text-align: right; font-weight: 600; font-variant-numeric: tabular-nums;">{v}</span></li>' for n,v in steps)+'</ol>'

VIS_A=[9,12,8,14,11,16,13,10,15,18,12,17,20,16]
VIS_B=[4,5,3,6,5,7,4,5,6,5,4,6,7,7]
CHECK=[('승인 대기 2일 넘음','가족방 a3f9c2e1 · 1명 · 2일 6시간','OpsFamily'),('용량 80% 넘음','가족방 7c21d4b0 · 4.3GB / 5GB','OpsFamily'),('7일 동안 아무도 안 봄','가족방 e5b81f73 · 마지막 방문 10월 25일','OpsFamily'),('탈퇴 예정','가족방 19d0a6c4 · 11월 6일 지워짐','OpsFamily')]

def home(side):
    sfx='{{sfx}}'
    checks='<ul style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column;">'+''.join(rowlink(a,b,f'{h}{sfx}.dc.html') for a,b,h in CHECK)+'</ul>'
    left=f'''{stats([('가족방','12'),('엄빠','18'),('가족 기기','41','승인 36 · 대기 5'),('사진·영상','3,210'),('저장 용량','21.4GB')],5 if side else 2)}
{card('방문',stats([('오늘 방문한 사람','23'),('오늘 방문','61회'),('7일 방문한 사람','47','엄빠 16 · 가족 31')],3)+bars('최근 14일 방문 수',('10월 22일','오늘'),VIS_A,VIS_B,'가족','엄빠'),'30분 안에 이어서 연 건 한 번으로 세요')}
{card('이번 주',kv([('새 가족방','2 <span style="color: var(--label-2); font-weight: 400;">(지난주 1)</span>'),('새로 들어온 가족','5 <span style="color: var(--label-2); font-weight: 400;">(지난주 3)</span>'),('올린 사진·영상','214 <span style="color: var(--label-2); font-weight: 400;">(지난주 188)</span>')]))}
{card('가족이 실제로 보는지',f'<p style="margin: 0; {NUM}">74%</p><meter class="sp-meter" min="0" max="100" value="74" style="width: 100%; height: 10px;">74%</meter>'+kv([('7일 안에 사진을 본 가족 기기','27 / 36'),('반응','88'),('한마디','17')]),'승인된 가족 기기 중 7일 안에 사진을 본 비율')}
{card('들어오다 멈춘 곳',funnel([('링크로 처음 방문',64),('이름 고름',40),('들어오기 신청',22),('승인',19)])+f'<p style="{SUB}">비밀번호 틀림 9번 · 승인 대기 기한 지남 2명</p>','최근 30일')}'''
    right=f'''{card('살펴볼 것',checks)}
{card('로그인 방법',kv([('카카오','11'),('네이버','4'),('구글','3')]))}
{card('홈 화면에 두기 부탁',kv([('7일 안','6'),('그 뒤 홈 화면에서 연 가족','4')]))}'''
    body=head('현황','11월 4일 오후 3:20 기준')
    if side:
        body+=f'\n<div style="display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 20px; align-items: start;"><div style="display: flex; flex-direction: column; gap: 20px; min-width: 0;">{left}</div><div style="display: flex; flex-direction: column; gap: 20px;">{right}</div></div>'
    else:
        body+='\n'+card('살펴볼 것',checks)+left+card('로그인 방법',kv([('카카오','11'),('네이버','4'),('구글','3')]))
    return shell('현황',body,side)

FAM=[('a3f9c2e1','10월 26일','2','6 / 1','412','3.1GB','34','오늘','오늘','정상'),
     ('7c21d4b0','10월 27일','2','9 / 0','1,284','4.3GB','58','어제','오늘','정상'),
     ('b0e4772a','10월 30일','1','4 / 0','236','1.2GB','21','11월 2일','어제','정상'),
     ('e5b81f73','10월 31일','1','2 / 0','48','0.3GB','0','10월 25일','10월 25일','정상'),
     ('19d0a6c4','11월 1일','1','3 / 0','91','0.6GB','2','11월 1일','11월 2일','탈퇴 예정'),
     ('5f3e90bb','11월 3일','2','1 / 2','12','0.1GB','9','어제','오늘','정상')]
COLS=['가족방','만든 날','엄빠','가족 승인 / 대기','사진·영상','용량','방문 7일','마지막 올림','마지막 방문','상태']

def families():
    sfx='{{sfx}}'
    th=''
    for i,c in enumerate(COLS):
        srt=' aria-sort="descending"' if c=='만든 날' else ''
        al='left' if i==0 else 'right' if i<9 else 'left'
        arrow='<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></path></svg>' if srt else ''
        th+=f'<th scope="col"{srt} style="padding: 0; text-align: {al}; font-weight: 500;"><a href="#" style="display: inline-flex; align-items: center; gap: 4px; min-height: 44px; padding: 0 12px; color: {"var(--pea-ink)" if srt else "var(--label-2)"}; text-decoration: none; font-size: 13px; line-height: 18px; white-space: nowrap;">{c}{arrow}</a></th>'
    rows=''
    for r in FAM:
        tds=f'<th scope="row" style="padding: 0 12px; text-align: left; font-weight: 600;"><a href="OpsFamily{sfx}.dc.html" style="display: inline-flex; align-items: center; min-height: 48px; color: var(--pea-ink); font-variant-numeric: tabular-nums;">{r[0]}</a></th>'
        for i,v in enumerate(r[1:9],1):
            tds+=f'<td style="padding: 0 12px; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap;">{v}</td>'
        st=r[9]
        badge=f'<span style="display: inline-flex; align-items: center; min-height: 24px; padding: 0 8px; border-radius: 999px; font-size: 13px; font-weight: 600; {"background: var(--fill); color: var(--danger);" if st!="정상" else "background: var(--pea-tint); color: var(--pea-deep);"}">{st}</span>'
        tds+=f'<td style="padding: 0 12px;">{badge}</td>'
        rows+=f'<tr style="border-top: 1px solid var(--separator);">{tds}</tr>'
    table=f'<div style="overflow-x: auto; border-radius: 16px; background: var(--surface);"><table style="width: 100%; border-collapse: collapse; font-size: 15px; line-height: 20px;"><caption style="position: absolute; width: 1px; height: 1px; overflow: hidden;">가족방 목록, 만든 날 최신순</caption><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'
    body=head('가족방','12곳 · 이름 대신 번호 앞 8자리로 보여요')+'\n'+table+f'\n<nav aria-label="쪽" style="display: flex; justify-content: center; gap: 8px;"><a href="#" style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 16px; border-radius: 12px; background: var(--fill); color: var(--label); text-decoration: none; font-size: 15px; font-weight: 600;">다음 50곳</a></nav>'
    return shell('가족방',body,True)

UP=[0,12,0,0,24,3,0,0,8,0,41,0,6,0,0,15,0,2,0,0,33,0,0,9,0,0,18,4,0,11]
VS=[3,5,2,4,6,5,3,2,5,4,8,3,4,5,2,6,4,3,2,4,9,5,3,6,4,3,7,5,4,6]
PEOPLE=[('엄빠 1','엄빠','—','22회','오늘'),('엄빠 2','엄빠','—','9회','어제'),('가족 기기 1','그룹 1','승인','14회','오늘'),('가족 기기 2','그룹 1','승인','11회','오늘'),('가족 기기 3','그룹 1','승인','6회','11월 2일'),('가족 기기 4','그룹 2','승인','3회','10월 31일'),('가족 기기 5','그룹 2','승인','0회','10월 27일'),('가족 기기 6','그룹 2','승인 대기','1회','11월 2일')]

def family():
    th=''.join(f'<th scope="col" style="padding: 0 12px; height: 44px; text-align: {"left" if i<3 else "right"}; font-size: 13px; font-weight: 500; color: var(--label-2); white-space: nowrap;">{c}</th>' for i,c in enumerate(['누구','그룹','상태','방문 30일','마지막 방문']))
    rows=''.join('<tr style="border-top: 1px solid var(--separator);">'+f'<th scope="row" style="padding: 0 12px; height: 48px; text-align: left; font-weight: 600;">{p[0]}</th><td style="padding: 0 12px;">{p[1]}</td><td style="padding: 0 12px; {"color: var(--danger); font-weight: 600;" if p[2]=="승인 대기" else ""}">{p[2]}</td>'+''.join(f'<td style="padding: 0 12px; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap;">{v}</td>' for v in p[3:])+'</tr>' for p in PEOPLE)
    people=f'<div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse; font-size: 15px; line-height: 20px;"><caption style="position: absolute; width: 1px; height: 1px; overflow: hidden;">사람별 방문, 이름 없이</caption><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'
    left=f'''{stats([('엄빠','2'),('가족','6','승인 5 · 대기 1'),('사진·영상','412','사진 398 · 영상 14'),('아이','2')],4)}
{card('최근 30일 올린 사진·영상',bars('최근 30일 올린 사진·영상 수',('10월 6일','오늘'),UP,unit='개'))}
{card('최근 30일 방문',bars('최근 30일 방문 수',('10월 6일','오늘'),VS))}
{card('사람별 방문',people,'이름은 안 보여요. 번호는 들어온 순서예요')}'''
    right=f'''{card('저장 용량','<p style="margin: 0; font-size: 17px; line-height: 24px; font-weight: 700;"><span style="font-size: 22px;">3.1GB</span> / 5GB</p><meter class="sp-meter" min="0" max="5" low="4" high="4.5" optimum="1" value="3.1" style="width: 100%; height: 8px;">3.1GB / 5GB</meter>')}
{card('그룹',kv([('그룹 1','4명'),('그룹 2','3명')]))}
{card('들어오기',kv([('공유 링크','3개'),('링크로 처음 방문','9'),('비밀번호 틀림','2번')]))}
{card('함께 관리','<p style="margin: 0; font-size: 15px; line-height: 20px;">엄빠 둘 · 10월 28일부터</p>')}'''
    body=f'''<a href="OpsFamilies{{{{sfx}}}}.dc.html" style="display: inline-flex; align-items: center; gap: 2px; min-height: 44px; width: max-content; color: var(--pea-ink); text-decoration: none; font-size: 15px;"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></path></svg>가족방</a>
<header style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h1 style="margin: 0; font-size: 34px; line-height: 41px; font-weight: 700; letter-spacing: -0.4px; font-variant-numeric: tabular-nums;">가족방 a3f9c2e1</h1><span style="display: inline-flex; align-items: center; min-height: 26px; padding: 0 10px; border-radius: 999px; background: var(--pea-tint); color: var(--pea-deep); font-size: 13px; font-weight: 600;">정상</span><p style="flex-basis: 100%; margin: 0; font-size: 15px; line-height: 20px; color: var(--label-2);">10월 26일에 만듦 · 마지막 올림 오늘 · 사진·이름·한마디는 안 보여요</p></header>
<div style="display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 20px; align-items: start;"><div style="display: flex; flex-direction: column; gap: 20px; min-width: 0;">{left}</div><div style="display: flex; flex-direction: column; gap: 20px;">{right}</div></div>'''
    return shell('가족방',body,True)

BOARDS=[('OpsHome','운영 · 현황 (PC)',lambda:home(True),1440,1360),
        ('OpsFamilies','운영 · 가족방 목록 (PC)',families,1440,600),
        ('OpsFamily','운영 · 가족방 상세 (PC)',family,1440,1420),
        ('OpsHomeMobile','운영 · 현황 (휴대폰, 위 메뉴 한 단)',lambda:home(False),390,2100)]
d=json.load(open('canvas.json')); b=d['boards']
Y0=max(v['y']+v['h'] for k,v in b.items() if not k.startswith('Ops'))+520
names=[]
for row,(theme,sfx,lab) in enumerate([('dark','','다크'),('light','-Light','라이트')]):
    x=0; y=Y0+row*(2100+120)
    for stem,title,fn,w,h in BOARDS:
        n=stem+sfx+'.dc.html'
        src=page(title,fn(),theme,w,h).replace('{{sfx}}',sfx)
        open(n,'w').write(src); names.append(n)
        b[n]={'x':x,'y':y,'w':w,'h':h,'title':f'{lab} · {title}'}
        if n not in d['order']: d['order'].append(n)
        x+=w+80
d['notes']['t-ops']={'kind':'title1','x':0,'y':Y0-300,'w':240,'maxW':4900,'text':'운영자 화면 1단계 (2026-11-04) · 현황·가족방·방문 · 위 다크, 아래 라이트'}
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print(Y0,names)
