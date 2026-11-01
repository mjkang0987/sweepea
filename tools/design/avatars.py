# 가족 캐릭터·자라는 아기 도트 그림(사용자 2026-11-01 보내 준 그림 "비슷하게 그릴 수 있겠어?" 시안).
# 32×32 칸 도트를 층(배경 원 → 옷 → 목 → 얼굴 → 머리카락 → 눈·볼·입 → 안경·모자)으로 쌓아 SVG로. 조합으로 여러 사람을 만든다.
# usage: python3 avatars.py <출력 폴더>  → <이름>.svg 와 모아 보기 sheet.html
import math, os, sys

W = 32
SKIN, SKIN_D = '#f6d3b8', '#e2ad8c'
EYE, MOUTH, BLUSH = '#3b2a22', '#c9605a', '#f4a3a3'
HAIR = {'brown': ('#7a4a2c', '#5c3620'), 'dark': ('#3e2a20', '#2a1c15'), 'gray': ('#c9c6c2', '#9e9a95'), 'navy': ('#2f3550', '#1f2338')}
BG = {'pink': '#fbd5dc', 'blue': '#cfe6f8', 'mint': '#cdf0dc', 'yellow': '#fbefc2', 'purple': '#e3d6f6', 'peach': '#f8dcc6'}


def blank():
    return [[None] * W for _ in range(W)]


def ell(g, cx, cy, rx, ry, c, rows=None):
    for y in range(W):
        if rows and not (rows[0] <= y <= rows[1]):
            continue
        for x in range(W):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                g[y][x] = c


def rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < W:
                g[y][x] = c


def outline(g, color, of):
    """of 색 칸의 바깥 가장자리(위·옆)에 한 칸 테두리"""
    out = [row[:] for row in g]
    for y in range(W):
        for x in range(W):
            if g[y][x] in of:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < W and (g[ny][nx] is None or g[ny][nx] in BG.values()):
                        out[ny][nx] = color
    return out


def person(hair='short', hc='brown', shirt='#4a86d8', bg='blue', glasses=False, cap=None, bow=None):
    g = blank()
    ell(g, 16, 16, 15.5, 15.5, BG[bg])                       # 배경 원
    h, hd = HAIR[hc]
    if hair in ('long', 'pigtails'):                         # 긴 머리는 얼굴 뒤로 어깨까지
        ell(g, 16, 18, 10.5, 10.5, h, rows=(10, 27))
    ell(g, 16, 33, 11.5, 7.5, shirt)                         # 옷(어깨)
    rect(g, 14, 24, 17, 26, SKIN_D)                          # 목
    g[27][15] = g[27][16] = SKIN_D                           # 목 파인 곳
    ell(g, 16, 17.5, 8.4, 7.9, SKIN)                         # 얼굴(크고 둥글게)
    if hair == 'curly':
        for cx, cy in ((9.5, 12), (12, 8.5), (16, 7.3), (20, 8.5), (22.5, 12), (8.8, 15.5), (23.2, 15.5)):
            ell(g, cx, cy, 3.6, 3.3, h)
        rect(g, 10, 10, 22, 12, h)
    else:
        ell(g, 16, 14.2, 9.6, 8.6, h, rows=(5, 13))           # 둥근 머리 덮개
        side = 19 if hair == 'short' else 22
        rect(g, 7, 13, 8, side, h); rect(g, 23, 13, 24, side, h)   # 옆머리
        for x in range(9, 23):                                # 앞머리: 가운데 가르마 쪽은 한 줄 짧게
            g[13][x] = h if x not in (15, 16) else g[13][x]
        g[14][9] = g[14][10] = g[14][21] = g[14][22] = h
    if hair == 'bun':
        ell(g, 16, 4.2, 3.4, 3.1, h)
    if hair == 'pigtails':
        ell(g, 6.5, 19, 2.8, 3.3, h); ell(g, 25.5, 19, 2.8, 3.3, h)
    for x, y in ((12, 8), (17, 7), (20, 9), (11, 11)):        # 머리카락 결
        if g[y][x] == h:
            g[y][x] = hd
    # 얼굴: 둥근 눈(2×2, 위 한 칸 반짝), 볼, 웃는 입
    for x0 in (12, 18):
        rect(g, x0, 17, x0 + 1, 18, EYE)
        g[17][x0 + 1] = '#ffffff'
    for x in (10, 11, 20, 21):
        g[20][x] = BLUSH
    g[21][15] = g[21][16] = MOUTH
    g[20][14] = g[20][17] = MOUTH
    if glasses:
        fr = '#9a5a35'
        for x0 in (10, 17):
            for x in range(x0, x0 + 5):
                g[16][x] = g[19][x] = fr
            for y in (17, 18):
                g[y][x0] = g[y][x0 + 4] = fr
        g[17][15] = g[17][16] = fr
    if cap:
        ell(g, 16, 13, 9.8, 7.6, cap, rows=(5, 12))
        rect(g, 7, 12, 25, 13, cap); rect(g, 22, 13, 27, 13, cap)   # 챙은 오른쪽으로 길게
        g[7][13] = g[7][14] = '#ffffff40'
    if bow:
        rect(g, 19, 6, 23, 8, bow); g[7][21] = '#ffffff'
    edge = '#5a3a2a'
    g = outline(g, edge, tuple(c for c in (h, shirt, cap, SKIN, SKIN_D) if c))
    return g


def baby(stage):
    """자라는 아기(맨 아래 줄): 1 강보, 5 서기 시안"""
    g = blank()
    ell(g, 16, 16, 15.5, 15.5, BG['yellow' if stage == 1 else 'blue'])
    h = HAIR['brown'][0]
    if stage == 1:
        ell(g, 17, 20, 11, 7.5, '#ffffff')                    # 강보
        ell(g, 13, 14.5, 6.5, 6.5, SKIN)                      # 얼굴(조금 기울게)
        ell(g, 12, 9, 2.5, 1.8, h)                            # 머리 한 줌
        rect(g, 9, 15, 10, 15, EYE); rect(g, 14, 15, 15, 15, EYE)   # 감은 눈
        g[17][9] = g[17][16] = BLUSH
        g[18][12] = MOUTH
        g = outline(g, '#00000022', ('#ffffff',))
    else:
        ell(g, 16, 25, 6, 5, '#ffffff', rows=(20, 29))        # 몸(내복)
        rect(g, 12, 27, 14, 29, SKIN); rect(g, 18, 27, 20, 29, SKIN)   # 다리
        rect(g, 8, 21, 10, 23, SKIN); rect(g, 22, 21, 24, 23, SKIN)    # 팔
        ell(g, 16, 13.5, 7, 6.8, SKIN)                        # 큰 머리
        ell(g, 16, 6, 2.2, 2, h); g[5][17] = h                # 정수리 머리카락
        for x in (13, 18):
            g[13][x] = g[14][x] = EYE
        g[16][11] = g[16][12] = g[16][19] = g[16][20] = BLUSH
        g[17][15] = g[17][16] = MOUTH
        g = outline(g, '#00000022', ('#ffffff',))
    return g


def svg(g, title):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" shape-rendering="crispEdges" role="img" aria-label="{title}">']
    for y in range(W):
        x = 0
        while x < W:
            c = g[y][x]
            if c is None:
                x += 1; continue
            run = 1
            while x + run < W and g[y][x + run] == c:
                run += 1
            fill = c if len(c) == 7 else c[:7]
            op = '' if len(c) == 7 else f' fill-opacity="{int(c[7:], 16) / 255:.2f}"'
            out.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{fill}"{op}/>')
            x += run
    out.append('</svg>')
    return ''.join(out)


SAMPLE = {
    'mom': ('엄마', person('long', 'brown', '#f2a7c3', 'pink')),
    'dad': ('아빠', person('short', 'dark', '#4a86d8', 'blue')),
    'grandma': ('할머니', person('curly', 'gray', '#f2a7c3', 'purple')),
    'grandpa': ('할아버지', person('short', 'gray', '#3f8f5a', 'mint', glasses=True)),
    'aunt': ('이모', person('bun', 'brown', '#b79ae8', 'yellow')),
    'uncle': ('삼촌', person('short', 'brown', '#2f7a4d', 'mint', cap='#2f3550')),
    'girl': ('양갈래', person('pigtails', 'brown', '#f6c94a', 'peach', bow='#f28aa8')),
    'baby1': ('아기 1단계(강보)', baby(1)),
    'baby5': ('아기 5단계(서기)', baby(5)),
}

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    cells = []
    for key, (name, g) in SAMPLE.items():
        s = svg(g, name)
        open(os.path.join(out, key + '.svg'), 'w').write(s)
        cells.append(f'<figure style="margin:0;text-align:center;font:13px sans-serif">{s.replace("<svg ", "<svg width=\"112\" height=\"112\" ")}<figcaption>{name}</figcaption></figure>')
    small = ''.join(s.replace('<svg ', '<svg width="40" height="40" ') for s in (svg(g, n) for n, g in SAMPLE.values()))
    open(os.path.join(out, 'sheet.html'), 'w').write(f'<body style="margin:16px;font:13px sans-serif"><div style="display:flex;gap:12px;flex-wrap:wrap">{"".join(cells)}</div><p>실제 크기(40px)</p><div style="display:flex;gap:8px">{small}</div></body>')
    print('ok', len(SAMPLE))
