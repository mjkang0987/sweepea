# 반응 도트 이모지 → 기기 기본 이모지(사용자 2026-10-27 "도트 느낌 말고 기본 이모지로", 디자인 145).
# 보드 안 도트 svg를 색으로 알아보고 같은 크기의 이모지 글자로 바꾼다. 못 알아본 건 그대로 두고 알려 준다
import os,re,glob
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
SIG=[('#ff5a7e','❤️'),('#4a90d9','👍'),('#ff9fb3','😊'),('#5bb8ff','😭'),('#ffe27a','✨')]
FONT="'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif"
changed=[]
for f in sorted(glob.glob('*.dc.html')):
    s=open(f).read(); n=0
    def rep(m):
        global n
        svg=m.group(0)
        ch=next((c for k,c in SIG if k in svg),None)
        if not ch: print('모름',f,svg[:120]); return svg
        w=int(re.search(r'width="(\d+)"',svg).group(1))
        n+=1
        return f'<span aria-hidden="true" style="display: inline-block; width: {w}px; height: {w}px; font-family: {FONT}; font-size: {round(w*0.9)}px; line-height: {w}px; text-align: center; vertical-align: middle;">{ch}</span>'
    t=re.sub(r'<svg[^>]*crispEdges[^>]*>.*?</svg>',rep,s,flags=re.S)
    if t!=s: open(f,'w').write(t); changed.append(f); print(f,n)
print(len(changed))
