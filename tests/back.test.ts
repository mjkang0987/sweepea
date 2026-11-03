import { test } from 'node:test';
import assert from 'node:assert/strict';
import { backHref, docHref } from '../src/lib/back.ts';

const at = (q = '') => new URL(`https://sweepea.co.kr/terms${q}`);

test('뒤로: ?from이 같은 사이트 경로면 그곳, 아니면 첫 화면(150)', () => {
  assert.equal(backHref(at(`?from=${encodeURIComponent('/login')}`)), '/login');
  assert.equal(backHref(at(`?from=${encodeURIComponent('/join/abc123')}`)), '/join/abc123');
  assert.equal(backHref(at()), '/');
  assert.equal(backHref(at('?from=//evil.example')), '/');
  assert.equal(backHref(at('?from=https://evil.example/')), '/');
  assert.equal(backHref(at('?from=/%5Cevil')), '/');
  assert.equal(backHref(at('?from=javascript:alert(1)')), '/');
  assert.equal(backHref(at('?from=/terms')), '/');
  assert.equal(docHref('/privacy', '/settings'), '/privacy?from=%2Fsettings');
});
