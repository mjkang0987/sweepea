import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BUCKET, TTL, expiryOf, leftOf } from '../src/lib/mediattl.ts';

const H = 3600;
const t0 = 1_800_000_000_000 - (1_800_000_000_000 % (BUCKET * 1000)); // 3시간 단위 시작(ms)

test('같은 3시간 안에서는 같은 만료(같은 주소), 다음 3시간이면 바뀜(135)', () => {
  assert.equal(BUCKET, 3 * H);
  assert.equal(TTL, 6 * H);
  assert.equal(expiryOf(t0), expiryOf(t0 + (3 * H - 1) * 1000));
  assert.notEqual(expiryOf(t0), expiryOf(t0 + 3 * H * 1000));
});

test('만료까지 남은 시간은 3~6시간', () => {
  assert.equal(leftOf(expiryOf(t0), t0), 6 * H);
  const late = t0 + (3 * H - 1) * 1000;
  assert.equal(leftOf(expiryOf(late), late), 3 * H + 1);
});

test('지난 만료·너무 먼 만료·숫자 아님은 0', () => {
  const now = t0;
  const nowSec = now / 1000;
  assert.equal(leftOf(nowSec - 1, now), 0);
  assert.equal(leftOf(nowSec, now), 0);
  assert.equal(leftOf(nowSec + TTL + 1, now), 0);
  assert.equal(leftOf(Number.NaN, now), 0);
  assert.equal(leftOf(nowSec + 1.5, now), 0);
  // 예전에 나간 2시간 주소도 남은 동안 열림
  assert.equal(leftOf(nowSec + 2 * H, now), 2 * H);
});
