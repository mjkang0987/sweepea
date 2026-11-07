import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addAge, HEALTH_ITEMS, healthState, monthDay, nextOf, splitSchedule } from '../src/lib/health.ts';

const item = (k: string) => HEALTH_ITEMS.find((i) => i.key === k)!;

test('생일에 개월·일 더하기(달 끝 맞춤)', () => {
  assert.equal(addAge('2025-09-17', { m: 12 }), '2026-09-17');
  assert.equal(addAge('2026-01-31', { m: 1 }), '2026-02-28');
  assert.equal(addAge('2025-09-17', { d: 14 }), '2025-10-01');
  assert.equal(addAge('2025-11-30', { m: 3 }), '2026-02-28');
});

test('권장 시기 상태: 13개월 아이', () => {
  const birth = '2025-09-17';
  const today = '2026-10-26';
  assert.deepEqual(healthState(item('je-1'), birth, today), { kind: 'now' });
  assert.deepEqual(healthState(item('dtap-4'), birth, today), { kind: 'soon', from: '2026-12-17' });
  assert.deepEqual(healthState(item('check-2'), birth, today), { kind: 'late' });
  // 12~15개월은 16개월이 되는 날부터 지남
  assert.deepEqual(healthState(item('mmr-1'), birth, '2027-01-16'), { kind: 'now' });
  assert.deepEqual(healthState(item('mmr-1'), birth, '2027-01-17'), { kind: 'late' });
});

test('다가오는 일정과 지난 일정', () => {
  const { upcoming, past } = splitSchedule('2025-09-17', '2026-10-26', new Map([['mmr-1', '2026-10-02']]));
  const keys = (l: typeof upcoming) => l.map((x) => x.item.key);
  assert.ok(!keys(upcoming).includes('mmr-1') && !keys(past).includes('mmr-1'), '한 것은 빠짐');
  assert.ok(keys(upcoming).includes('dtap-4') && keys(upcoming).includes('je-1'), '곧·지금 가능');
  assert.ok(keys(past).includes('rv-3'), '로타는 8개월이 지나면 시기 지남');
  assert.ok(!keys(upcoming).includes('dtap-5'), '6개월 넘게 남은 건 아직');
  assert.ok(keys(past).includes('hepb-1') && keys(past).includes('check-2'), '오래된 것·시기 지남은 지난 일정');
  assert.deepEqual(upcoming.map((x) => x.start), [...upcoming.map((x) => x.start)].sort());
});

test('A형간염 2차는 1차를 한 날 6개월 뒤부터', () => {
  const keys = (m: Map<string, string>, today: string) => splitSchedule('2025-09-17', today, m);
  assert.ok(!keys(new Map(), '2027-04-01').upcoming.some((x) => x.item.key === 'hepa-2'), '1차 전엔 안 보임');
  const after = keys(new Map([['hepa-1', '2027-07-17']]), '2027-09-17');
  const row = after.upcoming.find((x) => x.item.key === 'hepa-2')!;
  assert.equal(row.start, '2028-01-17');
  assert.deepEqual(row.state, { kind: 'soon', from: '2028-01-17' });
  const later = keys(new Map([['hepa-1', '2027-07-17']]), '2028-06-01');
  assert.ok(later.upcoming.some((x) => x.item.key === 'hepa-2'), '오래돼도 다가오는 일정');
});

test('다음 일정 하나: 아직이면 시작일·남은 날, 이미 가능하면 0', () => {
  const today = '2026-10-29';
  for (const birth of ['2025-11-08', '2026-08-30', '2024-01-10']) {
    const n = nextOf(birth, today, new Map());
    const want = splitSchedule(birth, today, new Map()).upcoming[0];
    assert.equal(n.what, want?.item.name ?? null);
    if (want?.state.kind === 'soon') {
      assert.equal(n.from, want.start);
      assert.equal(n.inDays, Math.round((Date.parse(want.start) - Date.parse(today)) / 86_400_000));
      assert.ok(n.inDays > 0);
    } else {
      assert.equal(n.from, null);
      assert.equal(n.inDays, 0);
    }
  }
});
test('다음 일정이 아직이면 시작일과 남은 날(앞 항목을 다 한 신생아)', () => {
  // 2026-09-20생, 10월 29일: B형간염 1·2차를 했으면 다음은 2개월 DTaP 1차(11월 20일부터, 22일 남음)
  const done = new Map([['hepb-1', '2026-09-20'], ['hepb-2', '2026-10-20']]);
  assert.deepEqual(nextOf('2026-09-20', '2026-10-29', done), { what: 'DTaP 1차', from: '2026-11-20', inDays: 22 });
});
test('월 일 글자', () => {
  assert.equal(monthDay('2026-12-07'), '12월 7일');
});
