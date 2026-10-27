# 한마디 시트 보드(CommentSheet, -Light)를 PhotoView 보드 위에 시트를 얹어 만든다
import os
os.chdir('/home/claude/sweepea/tools/canvas/project')
VH='position: absolute; width: 1px; height: 1px; overflow: hidden;'
def item(name,when,body,last=False,mine=False,confirm=False):
    head=('<div style="display: flex; align-items: center; gap: 8px;"><p style="flex: 1; margin: 0; font-size: 15px; line-height: 20px;"><strong style="font-weight: 700;">NAME</strong> <span style="color: var(--label-2);">· WHEN</span></p>'
          +('<details OPEN style="flex: none;"><summary aria-label="한마디 지우기" style="list-style: none; min-height: 44px; min-width: 44px; margin: -12px -10px -12px 0; display: flex; align-items: center; justify-content: center; color: var(--label-2); cursor: pointer;"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 12.5h9l1-12.5M10 11v5.5M14 11v5.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path></svg></summary></details>' if mine else '')
          +'</div>')
    conf=('<form style="display: flex; align-items: center; gap: 8px; margin-top: 6px; padding: 10px 12px; border-radius: 12px; background: var(--fill);"><span style="flex: 1; font-size: 15px; line-height: 20px;">이 한마디를 지울까요?</span>'
          '<button type="button" style="min-height: 44px; padding: 0 16px; border: 0; border-radius: 10px; background: var(--danger); color: var(--bg); font-family: inherit; font-size: 15px; font-weight: 700;">지우기</button></form>') if confirm else ''
    return ('<li style="padding: 14px 0; BORDERdisplay: flex; flex-direction: column; gap: 2px;">'+head+
      '<p style="margin: 0; font-size: 19px; line-height: 27px; word-break: keep-all; overflow-wrap: anywhere;">BODY</p>'+conf+'</li>').replace('BORDER','' if last else 'border-bottom: 0.5px solid var(--separator); ').replace('NAME',name).replace('WHEN',when).replace('BODY',body).replace('OPEN','open' if confirm else '')
for src,dst,back in [('PhotoView','CommentSheet','PhotoView'),('PhotoView-Light','CommentSheet-Light','PhotoView-Light')]:
    s=open(src+'.dc.html').read()
    s=s.replace('<title>사진 크게 보기</title>','<title>한마디 모두 보기</title>',1)
    s=s.replace('--panel:rgba(255,255,255,0.75);}','--panel:rgba(255,255,255,0.75);--danger:#d70015;}').replace('--panel:rgba(0,0,0,0.65);}','--panel:rgba(0,0,0,0.65);--danger:#ff6961;}')
    sheet=('<div aria-hidden="true" style="position: absolute; inset: 0; background: rgba(0,0,0,0.45);"></div>'
      '<section role="dialog" aria-modal="true" aria-labelledby="cs-title" style="position: absolute; left: 0; right: 0; bottom: 0; max-height: 72%; box-sizing: border-box; display: flex; flex-direction: column; background: var(--bg); border-radius: 20px 20px 0 0; box-shadow: 0 -8px 32px rgba(0,0,0,0.2);">'
      '<div aria-hidden="true" style="align-self: center; width: 40px; height: 5px; margin-top: 8px; border-radius: 3px; background: var(--fill);"></div>'
      '<header style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; padding: 4px 20px 8px;"><span></span>'
      '<h2 id="cs-title" style="margin: 0; font-size: 19px; line-height: 26px; font-weight: 700;">한마디 3개</h2>'
      '<a href="BACK.dc.html" style="justify-self: end; min-height: 56px; display: flex; align-items: center; color: var(--pea-ink); text-decoration: none; font-size: 19px; line-height: 26px; font-weight: 600;">닫기</a></header>'
      '<ul style="flex: 1; min-height: 0; overflow-y: auto; margin: 0; padding: 0 20px; list-style: none;">'
      + item('외할아버지','어제','아이고 우리 하린이 많이 컸네',mine=True,confirm=True)
      + item('엄마','어제','할아버지 보고 싶대요 🙂')
      + item('외할아버지','10월 22일','낮잠 자는 얼굴이 꼭 엄마 어릴 때 같다',True,mine=True) +
      '</ul>'
      '<form style="display: flex; gap: 8px; padding: 12px 20px 34px; border-top: 0.5px solid var(--separator);">'
      '<label for="cs-msg" style="VH">하린이에게 한마디</label>'
      '<input id="cs-msg" type="text" autocomplete="off" placeholder="하린이에게 한마디" style="flex: 1; min-width: 0; min-height: 56px; height: 56px; box-sizing: border-box; padding: 0 16px; border: 1.5px solid var(--field-border); border-radius: 10px; background: var(--bg); color: var(--label); font-family: inherit; font-size: 19px; line-height: 26px;">'
      '<button type="submit" style="flex: none; min-height: 56px; padding: 0 18px; border: 0; border-radius: 10px; background: var(--pea); color: var(--on-pea); font-family: inherit; font-size: 19px; line-height: 26px; font-weight: 700;">보내기</button></form>'
      '</section>').replace('BACK',back).replace('VH',VH)
    k=s.rfind('</main>'); s=s[:k]+sheet+'\n'+s[k:]
    s=s.replace('#pv-msg::placeholder{color:var(--label-2)}','#pv-msg::placeholder,#cs-msg::placeholder{color:var(--label-2)}',1)
    open(dst+'.dc.html','w').write(s)
print('sheets ok')
