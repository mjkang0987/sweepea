import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CHECKPOINTS, nextCheckpoint } from '../src/lib/milestones.ts';

test('발달 기준 시기: 지금 나이 바로 다음(같은 달이면 그 시기), 3살 넘으면 없음(153)', () => {
  assert.equal(nextCheckpoint(0)?.months, 2);
  assert.equal(nextCheckpoint(13)?.months, 15);
  assert.equal(nextCheckpoint(15)?.months, 15);
  assert.equal(nextCheckpoint(36)?.months, 36);
  assert.equal(nextCheckpoint(37), null);
  // 시기마다 네 영역이 다 있고 비어 있지 않음
  for (const c of CHECKPOINTS) for (const a of ['마음·관계', '말', '생각', '몸'] as const) assert.ok(c.items[a].length > 0, `${c.months} ${a}`);
});
