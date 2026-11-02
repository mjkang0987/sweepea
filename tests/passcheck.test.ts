import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parsePass, passStale } from '../src/lib/passcheck.ts';

const enc = (o: unknown) => btoa(JSON.stringify(o));
const now = 1_800_000_000;

test('출입증 쿠키 읽기', () => {
  assert.deepEqual(parsePass(enc({ access: 'a', refresh: 'r', expiresAt: now })), { access: 'a', refresh: 'r', expiresAt: now });
  assert.equal(parsePass(undefined), null);
  assert.equal(parsePass('깨진값'), null);
  assert.equal(parsePass(enc({ access: 'a', refresh: 'r' })), null);
});

test('갱신할 때가 됐나(미리 받기 거르기, 133)', () => {
  assert.equal(passStale(enc({ access: 'a', refresh: 'r', expiresAt: now + 3600 }), now), false);
  assert.equal(passStale(enc({ access: 'a', refresh: 'r', expiresAt: now + 61 }), now), false);
  assert.equal(passStale(enc({ access: 'a', refresh: 'r', expiresAt: now + 60 }), now), true);
  assert.equal(passStale(enc({ access: 'a', refresh: 'r', expiresAt: now - 10 }), now), true);
  assert.equal(passStale(undefined, now), false);
  assert.equal(passStale('깨진값', now), false);
});
