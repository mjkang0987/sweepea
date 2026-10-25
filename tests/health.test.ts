import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addAge, HEALTH_ITEMS, healthState, splitSchedule } from '../src/lib/health.ts';

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
  const { upcoming, past } = splitSchedule('2025-09-17', '2026-10-26', new Set(['mmr-1']));
  const keys = (l: typeof upcoming) => l.map((x) => x.item.key);
  assert.ok(!keys(upcoming).includes('mmr-1') && !keys(past).includes('mmr-1'), '한 것은 빠짐');
  assert.ok(keys(upcoming).includes('dtap-4') && keys(upcoming).includes('je-1'), '곧·지금 가능');
  assert.ok(!keys(upcoming).includes('dtap-5'), '6개월 넘게 남은 건 아직');
  assert.ok(keys(past).includes('hepb-1') && keys(past).includes('check-2'), '오래된 것·시기 지남은 지난 일정');
  assert.deepEqual(upcoming.map((x) => x.start), [...upcoming.map((x) => x.start)].sort());
});
