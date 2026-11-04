# 운영자 화면(164): 운영자만 열림(나머지 404), 방문 세기(링크 단계·가족 기기·봇 제외), 현황·목록·상세·기간·정렬·막대 숫자.
# 개발 서버는 OPS_USER_IDS=parent-ops 로 띄운다(.claude/launch.json sweepea-mock). 인자: 스크린샷 폴더(없으면 이 폴더)
import sys, os, base64, json, urllib.request
from playwright.sync_api import sync_playwright
B = 'http://localhost:4321'
OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))) + '/'
FAILS = []
def check(c, msg):
    print('ok' if c else 'FAIL', msg)
    if not c: FAILS.append(msg)
def passcookie(access):
    return base64.b64encode(json.dumps({'access': access, 'refresh': access, 'expiresAt': 9999999999}).encode()).decode()
def status(path, cookie=None, ua='Mozilla/5.0'):
    req = urllib.request.Request(B + path, headers={'user-agent': ua, **({'cookie': cookie} if cookie else {})})
    try:
        return urllib.request.urlopen(req).status
    except urllib.error.HTTPError as e:
        return e.code
OPS = 'sp_parent=' + passcookie('parent-ops')
HARIN = '00000000-0000-4000-8000-00000000f001'

# 1) 문: 로그인 안 함·다른 엄빠·없는 가족방·이상한 번호는 404
for path in ['/ops', '/ops/families', '/ops/families/' + HARIN]:
    check(status(path) == 404, f'{path} 로그인 안 하면 404')
    check(status(path, 'sp_parent=' + passcookie('parent-someone')) == 404, f'{path} 운영자 아닌 엄빠는 404')
    check(status(path, OPS) == 200, f'{path} 운영자는 열림')
check(status('/ops/families/00000000-0000-4000-8000-00000000ffff', OPS) == 404, '없는 가족방은 404')
check(status('/ops/families/abc', OPS) == 404, '번호 모양이 아니면 404')

with sync_playwright() as p:
    b = p.chromium.launch()
    # 2) 가족 기기: 링크 → 비밀번호 → 앨범(링크 두 단계 + 기기 방문). 미리보기 봇은 안 셈
    status('/i/Harin003', ua='kakaotalk-scrap/1.0')
    # 검사 브라우저 기본 이름(HeadlessChrome)은 봇으로 걸러져서 보통 아이폰 이름으로
    c = b.new_context(viewport={'width': 390, 'height': 844}, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148')
    pg = c.new_page()
    pg.goto(B + '/i/Harin001'); pg.get_by_role('button', name='외할머니').click(); pg.wait_for_url('**/password**')
    pg.fill('#pw', '1234'); pg.get_by_role('button', name='들어가기').click(); pg.wait_for_url('**/album')
    names = {k['name'] for k in c.cookies()}
    check({'sp_vl', 'sp_vp', 'sp_v'} <= names, '링크·비밀번호·앨범 방문 쿠키가 따로')
    check(all(k['httpOnly'] for k in c.cookies() if k['name'].startswith('sp_v')), '방문 쿠키는 httpOnly')
    pg.goto(B + '/album'); pg.goto(B + '/i/Harin001')  # 30분 안 다시 열기는 안 셈
    c.close()

    # 3) 운영자 화면
    c = b.new_context(viewport={'width': 1440, 'height': 1000})
    c.add_cookies([{'name': 'sp_parent', 'value': passcookie('parent-ops'), 'url': B}])
    pg = c.new_page()
    pg.goto(B + '/ops')
    check(pg.get_by_role('heading', name='현황', level=1).is_visible(), '현황 제목')
    check(pg.locator('.sp-o__nav-item[aria-current=page]').inner_text() == '현황', '메뉴에 지금 화면 표시')
    vis = pg.locator('section[aria-labelledby=sp-o-visits]')
    check(vis.locator('.sp-o__stat-num').first.inner_text() == '1', '방문한 사람 1(가족 기기, 다시 열기는 안 셈)')
    check(vis.locator('.sp-o__stat-num').nth(1).inner_text() == '1회', '방문 1회')
    check(pg.locator('.sp-o__bar').count() == 7, '기본 7일 막대 7개')
    tip = pg.locator('.sp-o__bar').last.locator('.sp-o__tip')
    check(not tip.is_visible(), '말풍선은 평소엔 숨김')
    pg.locator('.sp-o__bar').last.hover()
    check(tip.is_visible() and tip.inner_text() == '오늘 · 가족 1회 · 엄빠 0회', '막대에 올리면 그날 숫자 말풍선이 바로')
    tb, cb = tip.bounding_box(), pg.locator('.sp-o__chart').first.bounding_box()
    check(tb['x'] + tb['width'] <= cb['x'] + cb['width'] + 1 and tb['y'] >= cb['y'] - 1, '오른쪽 끝 막대 말풍선도 그래프 칸 안에')
    pg.screenshot(path=OUT + 'ops-1b-tip.png', clip={'x': cb['x'] - 20, 'y': cb['y'] - 20, 'width': cb['width'] + 40, 'height': cb['height'] + 40})
    pg.get_by_text('숫자로 보기').first.click()
    check(pg.locator('.sp-o__numbers[open] tbody tr').count() == 7, '숫자로 보기 표 7줄')
    steps = pg.locator('.sp-o__step .sp-o__kv-val').all_inner_texts()
    check(steps[:2] == ['1', '1'], f'링크 방문·비밀번호 화면 각각 1(봇 빼고) {steps}')
    pg.screenshot(path=OUT + 'ops-1-home.png', full_page=True)
    # 기간: 30일 → 막대 30개, 다른 화면으로 가도 기간 유지
    pg.get_by_role('link', name='30일').click(); pg.wait_for_url('**p=30d')
    check(pg.locator('.sp-o__bar').count() == 30, '30일 막대 30개')
    check(pg.get_by_role('link', name='가족방').get_attribute('href') == '/ops/families?p=30d', '메뉴 링크에 기간을 달고 다님')
    pg.goto(B + '/ops?p=90d')
    check(pg.locator('.sp-o__chart-scroll[tabindex="0"]').count() == 1 and '옆으로 밀면' in pg.content(), '90일은 좌우로 밀기 + 안내')
    sl = pg.evaluate("(() => { const e = document.querySelector('.sp-o__chart-scroll'); return [e.scrollWidth > e.clientWidth, e.querySelector('.sp-o__bar:last-child').getBoundingClientRect().right <= e.getBoundingClientRect().right + 1] })()")
    check(sl == [True, True], '넘치면 처음부터 오늘(오른쪽 끝)이 보임')
    # 밀어 둔 상태에서 가운데 막대 말풍선도 그래프 칸 안에(리뷰: 데이터 순서로 정렬하면 잘렸음)
    pg.set_viewport_size({'width': 375, 'height': 812}); pg.goto(B + '/ops?p=30d')
    pg.evaluate("document.querySelector('.sp-o__chart-scroll').scrollLeft = -200")
    bar = pg.locator('.sp-o__bar').nth(14); bar.hover()
    tb, cb = bar.locator('.sp-o__tip').bounding_box(), pg.locator('.sp-o__chart').first.bounding_box()
    check(tb['x'] >= cb['x'] - 1 and tb['x'] + tb['width'] <= cb['x'] + cb['width'] + 1, '밀어 둔 그래프의 말풍선도 칸 안에')
    pg.set_viewport_size({'width': 1440, 'height': 1000})
    pg.goto(B + '/ops'); pg.fill('input[name=from]', '2026-10-01'); pg.fill('input[name=to]', '2026-10-03'); pg.get_by_role('button', name='보기').click()
    pg.wait_for_url('**from=2026-10-01**')
    check(pg.locator('.sp-o__bar').count() == 3, '직접 고른 3일')
    # 목록 → 정렬 → 상세
    pg.goto(B + '/ops/families')
    rows = pg.locator('tbody .sp-o__tr')
    check(rows.count() >= 2, '가족방 줄')
    check('하린' not in pg.content() and '외할머니' not in pg.content(), '목록에 이름 없음')
    pg.get_by_role('link', name='방문', exact=True).click(); pg.wait_for_url('**sort=visits')
    check(pg.locator('th[aria-sort=descending]').inner_text().strip() == '방문', '정렬한 칸 표시')
    check(rows.first.locator('.sp-o__id').inner_text() == HARIN[:8], '방문 많은 가족방이 위')
    check(pg.get_by_role('link', name='30일').get_attribute('href') == '/ops/families?sort=visits&p=30d', '기간을 바꿔도 정렬 유지')
    pg.wait_for_timeout(500)
    pg.screenshot(path=OUT + 'ops-2-list.png', full_page=True)
    cell = rows.first.locator('td').nth(4)
    bg0 = cell.evaluate("e => getComputedStyle(e).backgroundColor")
    cell.hover(force=True)  # 줄 전체 링크가 위에 덮여 있음(의도)
    check(cell.evaluate("e => getComputedStyle(e).backgroundColor") != bg0, '목록 줄에 올리면 회색')
    cell.click(force=True); pg.wait_for_url('**/ops/families/' + HARIN)
    check(pg.url.endswith(HARIN), '줄 가운데(용량 칸)를 눌러도 상세로')
    check(pg.get_by_role('heading', level=1).inner_text() == '가족방 ' + HARIN[:8], '상세 제목은 번호')
    body = pg.locator('main').inner_text()
    check('외할머니' not in body and '하린' not in body and '외가' not in body, '상세에 이름·그룹 이름 없음')
    people = pg.locator('section[aria-labelledby=sp-o-people] tbody .sp-o__tr')
    check(people.count() >= 1 and '1회' in people.first.inner_text(), '사람별 방문(가족 기기 1, 1회)')
    pg.wait_for_timeout(500)  # 화면 넘김 애니메이션이 끝난 뒤
    pg.screenshot(path=OUT + 'ops-3-detail.png', full_page=True)
    # 좁은 화면: 위 메뉴 한 줄, 살펴볼 것이 먼저
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.goto(B + '/ops')
    nav = pg.locator('.sp-o__nav').bounding_box()
    check(nav['width'] >= 389 and nav['height'] < 60, '휴대폰은 위 메뉴 한 줄')
    check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), '휴대폰에서 옆으로 안 넘침')
    first = pg.locator('#sp-o-check').bounding_box()['y'] < pg.locator('#sp-o-visits').bounding_box()['y']
    check(first, '휴대폰은 살펴볼 것이 방문보다 위')
    pg.screenshot(path=OUT + 'ops-4-mobile.png', full_page=True)
    c.close(); b.close()
print('FAILS', FAILS)
