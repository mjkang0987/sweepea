import { test } from 'node:test';
import assert from 'node:assert/strict';
import { AVATARS, parseAvatar } from '../src/lib/avatar.ts';

test('parseAvatar: 폼 값 → 캐릭터 번호', () => {
  assert.equal(parseAvatar(''), null);
  assert.equal(parseAvatar('1'), 1);
  assert.equal(parseAvatar('45'), 45);
  for (const bad of ['0', '46', '07x', '-1', '1.5', ' 3', '100', null, undefined]) assert.equal(parseAvatar(bad), undefined, String(bad));
  assert.equal(AVATARS.length, 45);
});

test('initialOf: 마지막 낱말 첫 글자, 이모지도 한 글자로', async () => {
  const { initialOf } = await import('../src/lib/avatar.ts');
  assert.equal(initialOf('큰 이모'), '이');
  assert.equal(initialOf('외할머니'), '외');
  assert.equal(initialOf('😀할매'), '😀');
});
