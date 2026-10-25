import { test } from 'node:test';
import assert from 'node:assert/strict';
import { birthLabel, monthsOld, remainingLabel, seenLabel } from '../src/lib/age.ts';

test('생후 개월은 생일 날짜가 지나야 한 달 늘어난다', () => {
  assert.equal(monthsOld('2025-09-17', '2026-10-16'), 12);
  assert.equal(monthsOld('2025-09-17', '2026-10-17'), 13);
  assert.equal(monthsOld('2026-08-30', '2026-10-26'), 1);
  assert.equal(monthsOld('2026-10-26', '2026-10-26'), 0);
  assert.equal(monthsOld('2026-01-31', '2026-02-28'), 0);
});

test('생일 표시', () => {
  assert.equal(birthLabel('2025-09-07'), '2025년 9월 7일');
});

test('탈퇴까지 남은 시간', () => {
  const H = 3_600_000;
  assert.equal(remainingLabel(72 * H, 0), '3일 남았어요');
  assert.equal(remainingLabel(72 * H - 1, 0), '2일 23시간 남았어요');
  assert.equal(remainingLabel(29 * H + 59 * 60_000, 0), '1일 5시간 남았어요');
  assert.equal(remainingLabel(5 * H, 0), '5시간 남았어요');
  assert.equal(remainingLabel(H - 1, 0), '곧 지워져요');
  assert.equal(remainingLabel(-H, 0), '곧 지워져요');
  assert.equal(remainingLabel(NaN, 0), '곧 지워져요');
  assert.equal(remainingLabel(24 * H, 0), '1일 남았어요');
});

test('마지막으로 본 때는 서울 날짜로', () => {
  const now = Date.parse('2026-10-26T01:00:00+09:00');
  assert.equal(seenLabel('2026-10-26T00:10:00+09:00', now), '오늘');
  assert.equal(seenLabel('2026-10-25T23:50:00+09:00', now), '어제');
  assert.equal(seenLabel('2026-10-23T12:00:00+09:00', now), '3일 전');
});
