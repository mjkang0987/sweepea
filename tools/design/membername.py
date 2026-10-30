# 구성원 이름 바꾸기(사용자 2026-10-29 "이름 바꿀 수 있게 해줘, 접속한 사람"): MemberDetail 보드의 사람 줄 아래에 '부르는 이름' 칸 + [이름 바꾸기]
import os,re
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
FIELD=('<div style="flex: none; display: flex; flex-direction: column; gap: 8px;">'
       '<label for="m-name" style="font-size: 15px; line-height: 20px; font-weight: 600;">부르는 이름</label>'
       '<input id="m-name" type="text" value="하린 아빠" style="min-height: 52px; box-sizing: border-box; padding: 0 16px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px;">'
       '<span style="font-size: 13px; line-height: 18px; color: var(--label-2);">앨범·반응에 보이는 이름이에요. 그분 휴대폰에도 이 이름으로 보여요.</span>'
       '<button type="button" style="min-height: 52px; border: 0; border-radius: 12px; background: var(--fill); color: var(--label); font-family: inherit; font-size: 17px; font-weight: 600;">이름 바꾸기</button></div>\n    ')
for t in ['','-Light']:
    f=f'MemberDetail{t}.dc.html'; s=open(f).read()
    if 'id="m-name"' in s: continue
    i=s.index('<ul style="flex: none; list-style: none;'); s=s[:i]+FIELD+s[i:]
    open(f,'w').write(s)
print('ok')
