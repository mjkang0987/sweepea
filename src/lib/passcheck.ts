// 출입증 쿠키 값 읽기(부수 효과 없음): pass.ts와 미들웨어(미리 받기 거르기, 133)가 같이 쓰고 단위 검사로 본다
import type { Pass } from './backend/types';

/** 만료 이만큼(초) 전부터 갱신한다 */
export const REFRESH_EARLY = 60;

export function parsePass(raw: string | undefined): Pass | null {
  if (!raw) return null;
  try {
    const p = JSON.parse(atob(raw)) as Pass;
    return typeof p.access === 'string' && typeof p.refresh === 'string' && typeof p.expiresAt === 'number' ? p : null;
  } catch {
    return null;
  }
}

/** 갱신할 때가 된 출입증인가. 없거나 깨진 값은 false(갱신할 것이 없음) */
export function passStale(raw: string | undefined, nowSec = Date.now() / 1000): boolean {
  const p = parsePass(raw);
  return !!p && p.expiresAt - REFRESH_EARLY <= nowSec;
}
