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
