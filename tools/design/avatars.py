# 사용자가 보낸 캐릭터 그림(avatar-sheet.png, 2026-11-01)을 칸마다 원으로 잘라 앱 그림으로.
# 맨 아래 줄 아기 9단계 → public/kid/1~9.png(109, 자라는 아기). 가족 캐릭터(위 다섯 줄)는 110에서.
# usage: python3 tools/design/avatars.py   (저장소 맨 위에서)
import os
from PIL import Image, ImageDraw

SRC = 'tools/design/avatar-sheet.png'
OUT = 128  # 화면에선 48·64px로 보이므로 2배 이상
# 맨 아래 줄: 그림마다 가운데(x, y), 잘라 낼 반지름. 그림 칸 간격이 위 줄과 달라 하나씩(진한 칸이 몰린 자리에서 잼)
KIDS = [(94, 935), (247, 935), (395, 935), (545, 935), (704, 935), (852, 935), (994, 935), (1145, 935), (1294, 935)]
R = 72


def circle(img, cx, cy, r):
    c = img.crop((cx - r, cy - r, cx + r, cy + r)).resize((OUT, OUT), Image.LANCZOS)
    m = Image.new('L', (OUT * 4, OUT * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, OUT * 4 - 1, OUT * 4 - 1), fill=255)
    c.putalpha(m.resize((OUT, OUT), Image.LANCZOS))  # 가장자리 부드럽게
    return c


if __name__ == '__main__':
    src = Image.open(SRC).convert('RGB')
    os.makedirs('public/kid', exist_ok=True)
    for i, (cx, cy) in enumerate(KIDS, 1):
        circle(src, cx, cy, R).save(f'public/kid/{i}.png', optimize=True)
    print('ok', len(KIDS))
