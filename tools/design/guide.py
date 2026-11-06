# 자주 묻는 질문(181, 사용자 2026-11-06 "안내 화면" → /guide, 첫 화면 맨 아래 작은 링크 줄에서): 처리방침 글 모양 + 질문마다 펼치기
# 첫 질문만 펼친 모습. Landing 보드에도 앱처럼 맨 아래 작은 링크 줄(이용약관·처리방침·자주 묻는 질문)
import os,re,json
os.chdir(os.path.join(os.path.dirname(__file__),'..','canvas','project'))
QS=['할머니도 앱을 깔거나 가입해야 하나요?','링크가 다른 사람에게 가면 사진이 보이나요?','외가와 친가에 다른 사진을 보여 줄 수 있나요?','정말 무료인가요?','원본 화질로 올라가나요?','카톡으로 사진을 보내는 것과 뭐가 다른가요?','엄마·아빠 둘 다 올릴 수 있나요?','탈퇴하면 사진은 어떻게 되나요?']
A0='아니요. 엄마·아빠가 보낸 링크를 누르고 처음 한 번 이름을 고르고 그룹 비밀번호만 넣으면 돼요. 처음 쓰는 이름이면 엄마·아빠가 승인한 뒤 앨범이 열려요. 같은 휴대폰·같은 브라우저에서는 다음부터 링크만 누르면 돼요.'
CHEV=lambda r: f'<span aria-hidden="true" style="flex: none; width: 8px; height: 8px; border-right: 2px solid var(--label-3); border-bottom: 2px solid var(--label-3); transform: rotate({r}deg); margin: 0 4px;"></span>'
def page(t):
    rows=''
    for i,q in enumerate(QS):
        sep='' if i==0 else 'box-shadow: inset 0 1px 0 var(--separator);'
        a=f'<p style="margin: 0; padding: 0 16px 14px; font-size: 15px; line-height: 24px; color: var(--label-2);">{A0}</p>' if i==0 else ''
        rows+=f'<li style="{sep}"><p style="margin: 0; min-height: 52px; padding: 13px 16px; box-sizing: border-box; display: flex; align-items: center; gap: 12px; font-size: 17px; line-height: 24px; font-weight: 600;"><span style="flex: 1;">{q}</span>{CHEV(-135 if i==0 else 45)}</p>{a}</li>'
    return f'''<div class="sp-t sp-{{{{theme}}}}" style="position: relative; width: 390px; height: 844px; box-sizing: border-box; background: var(--bg); color: var(--label); font-family: 'Pretendard Variable', -apple-system, system-ui, sans-serif; display: flex; flex-direction: column; overflow: hidden; word-break: keep-all;">
  <main style="flex: 1; padding: 8px 20px 0; display: flex; flex-direction: column; gap: 12px;">
    <a href="Landing{t}.dc.html" style="min-height: 44px; display: flex; align-items: center; gap: 4px; color: var(--pea-ink); font-size: 17px; text-decoration: none;"><span aria-hidden="true" style="width: 9px; height: 9px; margin-left: 4px; border-left: 2.4px solid currentColor; border-bottom: 2.4px solid currentColor; transform: rotate(45deg);"></span>뒤로</a>
    <h1 style="margin: 0; font-size: 22px; line-height: 28px; font-weight: 800;">자주 묻는 질문</h1>
    <p style="margin: 0; font-size: 15px; line-height: 24px; color: var(--label-2);">스위피는 아기 사진을 올리고 카톡으로 링크만 보내면 할머니·할아버지가 앱 설치도 가입도 없이 보는 가족 앨범이에요.</p>
    <ul style="list-style: none; margin: 4px 0 0; padding: 0; border-radius: 12px; background: var(--surface); overflow: hidden;">{rows}</ul>
  </main>
  <div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 12px 20px 22px;">
    <a href="ParentLogin{t}.dc.html" style="min-height: 52px; border-radius: 12px; font-size: 17px; line-height: 22px; font-weight: 600; display: flex; align-items: center; justify-content: center; background: var(--pea); color: var(--on-pea); text-decoration: none; width: 100%; box-sizing: border-box;">무료로 시작하기</a>
    <p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">5GB까지 무료</p>
  </div>
</div>
'''
FINE=lambda t: f'<p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);"><a href="#" style="color: inherit;">이용약관</a> · <a href="#" style="color: inherit;">개인정보 처리방침</a> · <a href="Guide{t}.dc.html" style="color: inherit;">자주 묻는 질문</a></p>'
d=json.load(open('canvas.json')); b=d['boards']
for t in ['','-Light']:
    src=open(f'Landing{t}.dc.html').read()
    # 첫 화면 보드: 맨 아래 작은 링크 줄(앱 index.astro와 같게)
    src=re.sub(r'<p style="margin: 0; font-size: 13px; line-height: 18px; color: var\(--label-2\);"><a href="#".*?자주 묻는 질문</a></p>','',src)
    note='링크 받으셨나요? 로그인 없이 받은 링크를 눌러 주세요</p>'
    assert note in src
    src=src.replace(note,note+FINE(t),1)
    open(f'Landing{t}.dc.html','w').write(src)
    head=re.sub(r'<title>.*?</title>','<title>자주 묻는 질문</title>',src[:src.index('<div class="sp-t sp-{{theme}}"')],count=1)
    tail=src[src.index('</x-dc>'):]
    n=f'Guide{t}.dc.html'
    open(n,'w').write(head+page(t)+tail)
    ref=b[f'Landing{t}.dc.html']
    if n not in d['order']: d['order'].append(n)
    x=b[n]['x'] if n in b else max(v['x'] for v in b.values() if v['y']==ref['y'])+470
    b[n]=dict(ref,x=x,title=('다크' if not t else '라이트')+' · 자주 묻는 질문(/guide, 181)')
json.dump(d,open('canvas.json','w'),ensure_ascii=False,indent=1)
print('ok', b['Guide.dc.html'])
