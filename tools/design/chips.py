# 보드의 '위 하트 + 반응 4개'를 '반응 5개 알약(숫자)' 한 줄로 바꾼다. 사용: chips.py 파일... (칸 배경 변수는 원래 버튼 것을 따름)
import re,sys,os
os.chdir('/home/claude/sweepea/tools/canvas/project')
e=open('/home/claude/sweepea/src/lib/emoji.ts').read()
heart=re.search(r"heart: \{ label: '하트', anim: 'beat', svg: \"(.*?)\" \},",e).group(1).replace('\\"','"').replace(' aria-hidden="true" focusable="false"',' aria-hidden="true"').replace('width="32" height="32"','width="20" height="20"')
def chip(label,anim,svg,n,on,bg):
    st=('flex: 1; min-width: 0; min-height: 44px; padding: 0 6px; border: 0; border-radius: 22px; background: %s; %scolor: %s; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 4px; cursor: pointer;'
        % ('var(--pea-tint)' if on else bg, 'box-shadow: inset 0 0 0 1.5px var(--pea); ' if on else '', 'var(--pea-ink)' if on else 'var(--label)'))
    num='<span style="font-size: 15px; line-height: 20px; font-weight: 700;">%d</span>'%n if n else ''
    return '<button type="button" aria-pressed="%s" aria-label="%s %d개%s" style="%s"><span class="sp-%s" style="display: block; width: 20px; height: 20px;">%s</span>%s</button>'%('true' if on else 'false',label,n,', 내가 누름' if on else '',st,anim,svg,num)
counts={'최고':(1,False),'좋아':(0,False),'감동':(0,False),'반짝':(0,False)}
for f in sys.argv[1:]:
    p=f+'.dc.html'; s=open(p).read()
    a=s.find('<button type="button" aria-pressed="true" aria-label="하트 3개, 내가 누름"'); assert a>0,f
    b=s.find('</button>',a)+len('</button>'); s=s[:a].rstrip(' ')+s[b:]
    k=s.find('aria-label="최고 보내기"'); i=s.rfind('<div style="display: flex; gap: 8px;">',0,k); j=s.find('</div>',s.find('반짝 보내기',i))
    row=s[i:j]
    bg=re.search(r'aria-label="최고 보내기" style="[^"]*background: (var\(--\w+\))',row).group(1)
    btns=re.findall(r'<button type="button" aria-label="(\S+) 보내기"[^>]*><span class="sp-(\w+)"[^>]*>(<svg.*?</svg>)</span></button>',row,re.S)
    assert len(btns)==4,(f,len(btns))
    new='<div style="display: flex; gap: 6px;">'+chip('하트','beat',heart,3,True,bg)
    for label,anim,svg in btns:
        n,on=counts[label]; new+=chip(label,anim,svg.replace('width="22" height="22"','width="20" height="20"'),n,on,bg)
    s=s[:i]+new+s[j:]
    open(p,'w').write(s); print('ok',f,bg)
