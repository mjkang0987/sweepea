// 운영자 화면 문(164): ① Cloudflare Access 도장(서버가 직접 확인 — workers.dev는 Access를 안 거쳐 도장이 없음) ② 엄빠 로그인 ③ 운영자 명단.
// 하나라도 아니면 null → 화면은 404(그런 화면이 있다는 것도 안 알림). 개발 mock만 ①을 건너뛴다
import type { AstroCookies } from 'astro';
import { OPS_ACCESS_AUD, OPS_ACCESS_TEAM, OPS_USER_IDS, SWEEPEA_BACKEND } from 'astro:env/server';
import { getBackend } from './backend';
import { currentParent } from './pass';
import { inList, jwtKid, verifyAccessJwt, type AccessJwk } from './ops';

let jwks: { keys: AccessJwk[]; at: number } | undefined;
/** 열쇠는 Cloudflare가 가끔 바꾼다: 한 시간 기억. 도장의 kid가 기억한 열쇠에 없으면 1분에 한 번까지 다시 받는다 */
async function accessKeys(team: string, kid: string | undefined): Promise<AccessJwk[]> {
  const fresh = jwks && Date.now() - jwks.at < 3600_000 && (jwks.keys.some((k) => k.kid === kid) || Date.now() - jwks.at < 60_000);
  if (fresh) return jwks!.keys;
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
    const token = request.headers.get('cf-access-jwt-assertion');
    if (!token) return null;
    // 열쇠 받기 실패도 404로(500이면 이 화면이 있다는 게 드러난다)
    try {
      const keys = await accessKeys(OPS_ACCESS_TEAM, jwtKid(token));
      if (!(await verifyAccessJwt(token, { team: OPS_ACCESS_TEAM, aud: OPS_ACCESS_AUD, keys }))) return null;
    } catch {
      return null;
    }
  }
  const pass = await currentParent(cookies).catch(() => null);
  if (!pass) return null;
  const userId = await getBackend().userId(pass).catch(() => null);
  return inList(OPS_USER_IDS, userId) ? { userId: userId! } : null;
}
