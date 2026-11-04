import { test } from 'node:test';
import assert from 'node:assert/strict';
import { inList, isBot, parsePeriod, verifyAccessJwt, visitTarget, withPeriod, type AccessJwk } from '../src/lib/ops.ts';

const today = '2026-11-04';
const q = (s: string) => new URLSearchParams(s);

test('parsePeriod: 미리 정한 기간·직접 고르기·틀린 값은 7일', () => {
  assert.deepEqual(parsePeriod(q(''), today), { key: '7d', from: '2026-10-29', to: today, days: 7 });
  assert.deepEqual(parsePeriod(q('p=today'), today), { key: 'today', from: today, to: today, days: 1 });
  assert.deepEqual(parsePeriod(q('p=90d'), today), { key: '90d', from: '2026-08-07', to: today, days: 90 });
  assert.deepEqual(parsePeriod(q('from=2026-10-01&to=2026-10-31'), today), { key: 'custom', from: '2026-10-01', to: '2026-10-31', days: 31 });
  assert.equal(parsePeriod(q('p=1y'), today).key, '7d');
  assert.equal(parsePeriod(q('from=2026-11-05&to=2026-11-06'), today).key, '7d'); // 미래
  assert.equal(parsePeriod(q('from=2026-10-31&to=2026-10-01'), today).key, '7d'); // 거꾸로
  assert.equal(parsePeriod(q('from=2026-02-30&to=2026-03-01'), today).key, '7d'); // 없는 날
  assert.equal(parsePeriod(q('from=2025-01-01&to=2026-11-04'), today).key, '7d'); // 400일 넘음
  assert.equal(parsePeriod(q("from=2026-10-01'&to=2026-10-02"), today).key, '7d');
});

test('withPeriod: 기본 7일은 주소에 안 붙음', () => {
  assert.equal(withPeriod('/ops', parsePeriod(q(''), today)), '/ops');
  assert.equal(withPeriod('/ops', parsePeriod(q('p=30d'), today), 'sort=media'), '/ops?p=30d&sort=media');
  assert.equal(withPeriod('/ops/families', parsePeriod(q('from=2026-10-01&to=2026-10-02'), today)), '/ops/families?from=2026-10-01&to=2026-10-02');
});

test('inList·isBot·visitTarget', () => {
  assert.equal(inList(' a, b ', 'b'), true);
  assert.equal(inList('a,b', 'c'), false);
  assert.equal(inList('', ''), false);
  assert.equal(inList(undefined, null), false);
  assert.equal(isBot('kakaotalk-scrap/1.0'), true);
  assert.equal(isBot(null), true);
  assert.equal(isBot('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0) KAKAOTALK 10.0'), false);
  assert.deepEqual(visitTarget('GET', '/i/Harin001'), { kind: 'link', code: 'Harin001', step: 'link' });
  assert.deepEqual(visitTarget('GET', '/i/Harin001/password'), { kind: 'link', code: 'Harin001', step: 'link_pw' });
  assert.deepEqual(visitTarget('GET', '/album'), { kind: 'user' });
  assert.deepEqual(visitTarget('GET', '/home'), { kind: 'user' });
  for (const p of ['/ops', '/ops/families', '/api/views', '/m/x', '/auth/callback', '/', '/favicon.svg']) assert.equal(visitTarget('GET', p), null, p);
  assert.equal(visitTarget('POST', '/album'), null);
});

// 도장 만들기: 검사용 RSA 열쇠로 서명
const enc = (o: object) => Buffer.from(JSON.stringify(o)).toString('base64url');
async function signer() {
  const kp = (await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify'])) as CryptoKeyPair;
  const pub = (await crypto.subtle.exportKey('jwk', kp.publicKey)) as JsonWebKey;
  const keys: AccessJwk[] = [{ kid: 'k1', kty: 'RSA', n: pub.n!, e: pub.e! }];
  const sign = async (body: object, head: object = { alg: 'RS256', kid: 'k1' }) => {
    const data = `${enc(head)}.${enc(body)}`;
    const sig = Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', kp.privateKey, new TextEncoder().encode(data))).toString('base64url');
    return `${data}.${sig}`;
  };
  return { keys, sign };
}

test('verifyAccessJwt: 서명·발급처·받는 쪽·기한', async () => {
  const { keys, sign } = await signer();
  const team = 'pika.cloudflareaccess.com', aud = 'aud-1', nowSec = 1_800_000_000;
  const good = { iss: `https://${team}`, aud: [aud], exp: nowSec + 60 };
  const o = { team, aud, keys, nowSec };
  assert.equal(await verifyAccessJwt(await sign(good), o), true);
  assert.equal(await verifyAccessJwt(null, o), false);
  assert.equal(await verifyAccessJwt('a.b.c', o), false);
  assert.equal(await verifyAccessJwt(await sign({ ...good, exp: nowSec - 1 }), o), false); // 기한 지남
  assert.equal(await verifyAccessJwt(await sign({ ...good, aud: ['other'] }), o), false); // 받는 쪽 다름
  assert.equal(await verifyAccessJwt(await sign({ ...good, iss: 'https://evil.cloudflareaccess.com' }), o), false);
  assert.equal(await verifyAccessJwt(await sign(good, { alg: 'none', kid: 'k1' }), o), false);
  assert.equal(await verifyAccessJwt(await sign(good, { alg: 'RS256', kid: 'k2' }), o), false); // 모르는 열쇠
  const t = await sign(good);
  const forged = t.split('.');
  forged[1] = enc({ ...good, aud: [aud, 'x'], exp: nowSec + 9999 });
  assert.equal(await verifyAccessJwt(forged.join('.'), o), false); // 본문 바꿔치기
  const other = await signer();
  assert.equal(await verifyAccessJwt(await other.sign(good), o), false); // 다른 열쇠로 서명
});
