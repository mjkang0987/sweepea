# 183 빈 앨범 가운데 '사진 추가하기'(웹 UX 점검 2026-11-03): ParentEmpty를 유리 탭바로 바꾸고(102 glass(), 떠 있던 알약은 거기서 빠짐)
# 안내 글 아래에 채운 버튼(웹 .sp-p__btn·.sp-p__empty-btn, SendSetupEmpty와 같은 모양) 하나. 라이트·다크
import os
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'glasstab.py')).read()
exec(src[:src.index('SYR=')])  # glass()만(glasstab.py는 불러오면 보드를 다시 만듦)
for t in ['','-Light']:
    n=f'ParentEmpty{t}.dc.html'; glass(n,n,'앨범 · 사진 없음',t)
    s=open(n).read(); anchor='설치 없이 바로 보실 수 있어요</p>'
    assert s.count(anchor)==1 and 'sp-glass-tint" style="position: absolute; left: 50%' not in s
    btn=(f'\n      <a href="ParentUpload{t}.dc.html" style="align-self: stretch; margin-top: 8px; min-height: 52px; padding: 0 20px; display: flex; align-items: center; justify-content: center; '
         'border-radius: 12px; background: var(--pea); color: var(--on-pea); text-decoration: none; font-size: 17px; line-height: 22px; font-weight: 700;">사진 추가하기</a>'
         # 웹에 원래 있던 비밀번호 안내(보드엔 없던 차이)
         '\n      <p style="margin: 0; font-size: 13px; line-height: 18px; color: var(--label-2);">처음 들어올 때 한 번 가족 비밀번호 4자리를 물어요. 비밀번호도 같이 알려 주세요.</p>')
    s=s.replace(anchor,anchor+btn).replace('설치 없이 바로 보실 수 있어요','설치 없이 보실 수 있어요')  # 웹 문구와 같게
    open(n,'w').write(s)
print('ok')
