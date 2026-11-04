// 운영자 화면 문(164): ① Cloudflare Access 도장(서버가 직접 확인 — workers.dev는 Access를 안 거쳐 도장이 없음) ② 엄빠 로그인 ③ 운영자 명단.
// 하나라도 아니면 null → 화면은 404(그런 화면이 있다는 것도 안 알림). 개발 mock만 ①을 건너뛴다
import type { AstroCookies } from 'astro';
import { OPS_ACCESS_AUD, OPS_ACCESS_TEAM, OPS_USER_IDS, SWEEPEA_BACKEND } from 'astro:env/server';
import { getBackend } from './backend';
import { currentParent } from './pass';
import { inList, verifyAccessJwt, type AccessJwk } from './ops';

let jwks: { keys: AccessJwk[]; at: number } | undefined;
async function accessKeys(team: string): Promise<AccessJwk[]> {
  // 열쇠는 Cloudflare가 가끔 바꾼다: 한 시간 기억
  if (jwks && Date.now() - jwks.at < 3600_000) return jwks.keys;
  const res = await fetch(`https://${team}/cdn-cgi/access/certs`, { signal: AbortSignal.timeout(5000) });
  if (!res.ok) throw new Error(`access certs ${res.status}`);
  jwks = { keys: ((await res.json()) as { keys: AccessJwk[] }).keys, at: Date.now() };
  return jwks.keys;
}

const devSkipAccess = () => !import.meta.env.PROD && SWEEPEA_BACKEND === 'mock';

export async function opsGate(request: Request, cookies: AstroCookies): Promise<{ userId: string } | null> {
  if (!OPS_USER_IDS) return null;
  if (!devSkipAccess()) {
    if (!OPS_ACCESS_TEAM || !OPS_ACCESS_AUD) return null;
    const ok = await verifyAccessJwt(request.headers.get('cf-access-jwt-assertion'), { team: OPS_ACCESS_TEAM, aud: OPS_ACCESS_AUD, keys: await accessKeys(OPS_ACCESS_TEAM) }).catch(() => false);
    if (!ok) return null;
  }
  const pass = await currentParent(cookies).catch(() => null);
  if (!pass) return null;
  const userId = await getBackend().userId(pass);
  return inList(OPS_USER_IDS, userId) ? { userId: userId! } : null;
}
