import { test } from 'node:test';
import assert from 'node:assert/strict';
import { installPlatform } from '../src/lib/install.ts';

test('기기 종류', () => {
  assert.equal(installPlatform('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 KAKAOTALK 10.8.0'), 'kakao');
  assert.equal(installPlatform('Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36;KAKAOTALK 2410800'), 'kakao');
  assert.equal(installPlatform('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'), 'ios');
  assert.equal(installPlatform('Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/129.0 Mobile Safari/537.36'), 'android');
  assert.equal(installPlatform('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'), 'other');
});
