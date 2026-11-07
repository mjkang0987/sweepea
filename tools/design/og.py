# 카톡·검색 미리보기 그림(113): 1200×630 public/og.png. 콩이 + 스위피 + 첫 화면 제목 문구를 가운데 세로로(가운데 정사각형으로 잘려도 보이게)
# usage: python3 tools/design/og.py <PretendardVariable.woff2 경로>   (저장소 맨 위에서. 글꼴은 디자인 캔버스 ds/sweepea/fonts에 있음)
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

font = base64.b64encode(pathlib.Path(sys.argv[1]).read_bytes()).decode()
kongi = base64.b64encode(pathlib.Path('public/kongi-crop.svg').read_bytes()).decode()
html = f'''<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url(data:font/woff2;base64,{font}) format("woff2-variations");font-weight:45 920}}
.og{{margin:0;width:1200px;height:630px;background:#e7f1f0;color:#1d1d1f;font-family:P;display:flex;flex-direction:column;align-items:center;justify-content:center;word-break:keep-all}}
.og-kongi{{height:176px;image-rendering:pixelated;margin-bottom:28px}}
.og-name{{margin:0;font-size:88px;line-height:1.1;font-weight:800;color:#0f766e;letter-spacing:-0.02em}}
.og-line{{margin:16px 0 0;font-size:40px;line-height:1.3;font-weight:600;letter-spacing:-0.01em}}
</style><body class="og"><img class="og-kongi" src="data:image/svg+xml;base64,{kongi}" alt=""><p class="og-name">스위피</p><p class="og-line">아기 사진, 단톡방 말고 가족 앨범에</p></body>'''

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.set_content(html)
    pg.evaluate('document.fonts.ready')
    pg.screenshot(path='public/og.png')
    b.close()
print('ok public/og.png')
