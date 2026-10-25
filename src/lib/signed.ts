// 사진 파일 주소에 서명을 붙인다. 앨범을 그리는 서버(RLS로 볼 수 있는 것만 받음)가 서명하고,
// /m/<키>는 서명·만료만 확인해 DB를 부르지 않는다. 부모가 기기를 막아도 이미 받은 주소는 만료(최대 2시간)까지 열린다
import { MEDIA_URL_SECRET } from 'astro:env/server';

const enc = new TextEncoder();
let devSecret: string | undefined;
let cached: { secret: string; key: Promise<CryptoKey> } | undefined;

function hmacKey(): Promise<CryptoKey> {
  const secret = MEDIA_URL_SECRET || (import.meta.env.PROD ? '' : (devSecret ??= crypto.randomUUID()));
  if (!secret) throw new Error('MEDIA_URL_SECRET가 없다');
  if (cached?.secret !== secret) {
    cached = { secret, key: crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']) };
  }
  return cached.key;
}

async function sign(msg: string): Promise<string> {
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', await hmacKey(), enc.encode(msg)));
  return btoa(String.fromCharCode(...sig)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

const HOUR = 3600;
const TTL = 2 * HOUR;

/** 만료를 시간 단위로 맞춰 한 시간 동안은 같은 주소(브라우저 캐시). 만료까지 1~2시간 */
export async function signedMediaUrl(key: string, nowMs = Date.now()): Promise<string> {
  const e = Math.floor(nowMs / 1000 / HOUR) * HOUR + TTL;
  return `/m/${key}?e=${e}&s=${await sign(`${key}:${e}`)}`;
}

/** 맞으면 남은 초, 틀리거나 만료면 0 */
export async function verifyMediaUrl(key: string, e: string | null, s: string | null, nowMs = Date.now()): Promise<number> {
  const exp = Number(e);
  const left = exp - Math.floor(nowMs / 1000);
  if (!s || !Number.isInteger(exp) || left <= 0 || left > TTL) return 0;
  const want = await sign(`${key}:${exp}`);
  // 길이·내용을 한 글자씩 끝까지 비교(시간으로 서명을 맞혀 보지 못하게)
  let diff = want.length ^ s.length;
  for (let i = 0; i < want.length; i++) diff |= want.charCodeAt(i) ^ (s.charCodeAt(i) || 0);
  return diff === 0 ? left : 0;
}
