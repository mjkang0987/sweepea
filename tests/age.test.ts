import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ageLabel, agoLabel, birthLabel, dayMark, kidImage, kidStage, milestone, monthsOld, nextMark, photoAge, remainingLabel, seenLabel } from '../src/lib/age.ts';

test('kidStage: 나이별 아기 그림 단계', () => {
  const b = '2025-01-01';
  assert.equal(kidStage(b, '2024-12-31'), 1); // 태어나기 전
  assert.equal(kidStage(b, '2025-04-10'), 1); // 100일째
  assert.equal(kidStage(b, '2025-04-11'), 2); // 101일
  assert.equal(kidStage(b, '2025-07-01'), 3); // 6개월
  assert.equal(kidStage(b, '2025-09-01'), 4); // 8개월
  assert.equal(kidStage(b, '2026-01-01'), 5); // 첫돌
  assert.equal(kidStage(b, '2026-07-01'), 6); // 18개월
  assert.equal(kidStage(b, '2027-01-01'), 7); // 2세
  assert.equal(kidStage(b, '2028-01-01'), 8); // 3세
  assert.equal(kidStage(b, '2031-12-31'), 8); // 7세 전날
  assert.equal(kidStage(b, '2032-01-01'), 9); // 7세
  assert.equal(kidImage(null, '2026-01-01'), '/kongi.svg');
  assert.equal(kidImage(b, '2026-01-01'), '/kid/5.png');
});

test('photoAge: 찍은 날의 생후 나이', () => {
  assert.equal(photoAge('2025-09-17', '2026-10-21'), '생후 13개월');
  assert.equal(photoAge('2026-10-01', '2026-10-01'), '생후 1일');
  assert.equal(photoAge('2026-10-01', '2026-10-30'), '생후 30일');
  assert.equal(photoAge('2026-10-01', '2026-11-01'), '생후 1개월');
  assert.equal(photoAge('2026-10-01', '2026-09-30'), null);
  // 달 끝 생일: 다음 달엔 그 날이 없어 한 달이 안 참
  assert.equal(photoAge('2026-01-31', '2026-02-28'), '생후 29일');
  assert.equal(photoAge('2026-01-31', '2026-03-01'), '생후 1개월');
});

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

test('지난 시간', () => {
  const now = Date.parse('2026-10-26T12:00:00+09:00');
  assert.equal(agoLabel('2026-10-26T11:59:30+09:00', now), '방금');
  assert.equal(agoLabel('2026-10-26T11:50:00+09:00', now), '10분 전');
  assert.equal(agoLabel('2026-10-26T09:00:00+09:00', now), '3시간 전');
  assert.equal(agoLabel('2026-10-25T09:00:00+09:00', now), '어제');
  assert.equal(agoLabel('2026-10-22T09:00:00+09:00', now), '4일 전');
});

test('백일·돌·생일은 그날만', () => {
  assert.equal(milestone('2026-07-19', '2026-10-26'), '태어난 지 100일이에요');
  assert.equal(milestone('2026-07-18', '2026-10-26'), null);
  assert.equal(milestone('2025-10-26', '2026-10-26'), '첫돌이에요');
  assert.equal(milestone('2024-10-26', '2026-10-26'), '두 돌이에요');
  assert.equal(milestone('2026-10-26', '2026-10-26'), null);
  assert.equal(milestone('2025-10-25', '2026-10-26'), null);
});

test('앨범 머리 나이: N개월 N일', () => {
  assert.equal(ageLabel('2025-01-03', '2026-10-29'), '21개월 26일');
  assert.equal(ageLabel('2025-01-03', '2026-11-03'), '22개월');
  assert.equal(ageLabel('2026-10-20', '2026-10-29'), '9일');
  assert.equal(ageLabel('2026-10-29', '2026-10-29'), '0일');
  assert.equal(ageLabel('2026-01-31', '2026-03-02'), '1개월 2일');
  assert.equal(ageLabel('2026-11-01', '2026-10-29'), null);
  // 달 생일이 없는 달은 그 달 마지막 날이 달 생일
  assert.equal(ageLabel('2026-01-31', '2026-02-28'), '1개월');
  assert.equal(ageLabel('2026-03-31', '2026-04-30'), '1개월');
  assert.equal(ageLabel('2024-02-29', '2025-02-28'), '12개월');
  assert.equal(ageLabel('2024-02-29', '2028-02-29'), '48개월');
});

test('기념일 표시: 50일, 100~1000일 백 단위, 그다음은 돌만', () => {
  assert.equal(dayMark('2026-01-01', '2026-02-19'), '50일');
  assert.equal(dayMark('2025-01-01', '2027-09-27'), '1000일');
  assert.equal(dayMark('2025-01-01', '2028-06-23'), null); // 1270일째(2000일 같은 건 안 침)
  assert.equal(dayMark('2026-07-19', '2026-10-26'), '100일');
  assert.equal(dayMark('2026-01-01', '2026-07-19'), '200일');
  assert.equal(dayMark('2025-01-01', '2026-05-15'), '500일');
  assert.equal(dayMark('2025-01-03', '2026-01-03'), '첫돌');
  assert.equal(dayMark('2024-01-03', '2026-01-03'), '두 돌');
  assert.equal(dayMark('2025-01-03', '2026-01-04'), null);
  assert.equal(milestone('2026-01-01', '2026-07-19'), '태어난 지 200일이에요');
});

test('nextMark: 오늘 또는 다음 기념일과 남은 날(153)', () => {
  // 2025-09-17생: 400일 = 2026-10-21, 500일 = 2027-01-29, 첫돌 = 2026-09-17
  assert.deepEqual(nextMark('2025-09-17', '2026-11-03'), { mark: '500일', day: '2027-01-29', inDays: 87 });
  assert.deepEqual(nextMark('2025-09-17', '2026-10-21'), { mark: '400일', day: '2026-10-21', inDays: 0 });
  assert.deepEqual(nextMark('2025-09-17', '2026-09-10'), { mark: '첫돌', day: '2026-09-17', inDays: 7 });
  assert.deepEqual(nextMark('2025-09-17', '2025-09-17'), { mark: '50일', day: '2025-11-05', inDays: 49 });
  // 1000일 뒤에는 돌만
  assert.deepEqual(nextMark('2020-01-10', '2026-11-03'), { mark: '일곱 돌', day: '2027-01-10', inDays: 68 });
  assert.equal(nextMark('2010-01-01', '2026-11-03'), null);
});
