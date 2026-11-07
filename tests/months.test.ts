import { test } from 'node:test';
import assert from 'node:assert/strict';
import { groupYears } from '../src/lib/months.ts';

const rep = (id: string) => ({ id, kind: 'photo' as const, thumb_key: id, width: 1, height: 1 });

test('연별: 달을 해마다 합치고 기간·대표 5장(달마다 1번 먼저)', () => {
  const ys = groupYears([
    { ym: '2026-10', n: 26, reps: [rep('a1'), rep('a2'), rep('a3')] },
    { ym: '2026-03', n: 10, reps: [rep('b1'), rep('b2')] },
    { ym: '2025-12', n: 4, reps: [rep('c1')] },
  ]);
  assert.equal(ys.length, 2);
  assert.deepEqual({ y: ys[0].y, n: ys[0].n, from: ys[0].from, to: ys[0].to, last: ys[0].last }, { y: '2026', n: 36, from: 3, to: 10, last: '2026-10' });
  assert.deepEqual(ys[0].reps.map((r) => r.id), ['a1', 'b1', 'a2', 'b2', 'a3']);
  assert.deepEqual(ys[1].reps.map((r) => r.id), ['c1']);
});
