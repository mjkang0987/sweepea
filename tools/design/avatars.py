# 사용자가 보낸 캐릭터 그림(avatar-sheet.png, 2026-11-01)을 칸마다 원으로 잘라 앱 그림으로.
# 맨 아래 줄 아기 9단계 → public/kid/1~9.png(109, 자라는 아기). 가족 캐릭터(위 다섯 줄 45명) → public/avatar/1~45.webp(110). 맨 아래 강아지는 안 씀(사용자 "빼기")
# usage: python3 tools/design/avatars.py   (저장소 맨 위에서)
import os
from PIL import Image, ImageDraw

SRC = 'tools/design/avatar-sheet.png'
OUT = 128  # 화면에선 48·64px로 보이므로 2배 이상
# 맨 아래 줄: 그림마다 가운데(x, y), 잘라 낼 반지름. 그림 칸 간격이 위 줄과 달라 하나씩(진한 칸이 몰린 자리에서 잼)
KIDS = [(94, 935), (247, 935), (395, 935), (545, 935), (704, 935), (852, 935), (994, 935), (1145, 935), (1294, 935)]
R = 72
# 위 다섯 줄: 9칸씩, 칸 가운데 x·y(그림 칸 간격이 고르다), 반지름 78
COLS = [108, 272, 437, 602, 767, 932, 1097, 1262, 1427]
ROWS = [110, 275, 440, 605, 768]
# 캐릭터가 원본 칸 가운데에서 옆으로 치우친 것(사용자 2026-11-01 "캐릭터 중앙 안 맞는 경우"): 두 눈 가운데를 원 가운데로. 눈 사이 30~40px로 찾은 값, 21·30·31은 눈으로 본 값
SHIFT = {8: 3, 17: 3, 18: 3, 20: -4, 22: -14, 23: -4, 28: -4, 34: 4, 35: 5, 36: 4, 39: -4, 42: 3, 43: 4, 44: 6, 45: 6, 21: -8, 31: -10, 30: -9}


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
    os.makedirs('public/avatar', exist_ok=True)
    people = [(x + SHIFT.get(i, 0), y, 78) for i, (x, y) in enumerate(((x, y) for y in ROWS for x in COLS), 1)]
    for i, (cx, cy, r) in enumerate(people, 1):
        # 가족 캐릭터는 고르기 화면에 45개가 한꺼번에 떠서 작게(96px WebP, 화면 40~48px의 2배)
        circle(src, cx, cy, r).resize((96, 96), Image.LANCZOS).save(f'public/avatar/{i}.webp', quality=88, method=6)
    print('ok', len(KIDS), len(people))
