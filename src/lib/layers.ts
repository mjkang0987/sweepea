// 가운데 레이어: 같은 일은 한 번만. "봤음"은 기기 쿠키에(DB 칸 없이). 버튼은 폼 POST로 적는다
import type { AstroCookies } from 'astro';

export const JOIN_SEEN = 'sp_join_seen';
export const WAITED = 'sp_waited';
export const PHOTOS_SEEN = 'sp_photos_seen';
export const MILESTONE_SEEN = 'sp_milestone_seen';
export const STORAGE_SEEN = 'sp_storage_seen';

const opts = { path: '/', httpOnly: true, sameSite: 'lax' as const, secure: import.meta.env.PROD, maxAge: 365 * 24 * 3600 };

export const setLayerCookie = (cookies: AstroCookies, name: string, value: string) => cookies.set(name, value, opts);

/** 쿠키에 적힌 시각(ISO). 없거나 깨졌으면 null */
export function seenAt(cookies: AstroCookies, name: string): number | null {
  const v = cookies.get(name)?.value;
  const t = v ? Date.parse(v) : NaN;
  return Number.isFinite(t) ? t : null;
}
