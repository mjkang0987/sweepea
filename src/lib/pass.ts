// 출입증: 이 기기의 익명 세션을 httpOnly 쿠키에 담는다. 브라우저 JS는 읽지 못한다.
import type { AstroCookies } from 'astro';
import { getBackend, type Pass } from './backend';

const PASS = 'sp_pass';
const SIZE = 'sp_size';
// 크롬은 쿠키 수명을 400일로 자른다. 들어올 때마다 다시 써서 늘린다
const MAX_AGE = 400 * 24 * 3600;

export type TextSize = 'base' | 'large' | 'xlarge';

function write(cookies: AstroCookies, pass: Pass) {
  cookies.set(PASS, btoa(JSON.stringify(pass)), {
    path: '/',
    httpOnly: true,
    secure: import.meta.env.PROD,
    sameSite: 'lax',
    maxAge: MAX_AGE,
  });
}

function read(cookies: AstroCookies): Pass | null {
  const raw = cookies.get(PASS)?.value;
  if (!raw) return null;
  try {
    const p = JSON.parse(atob(raw)) as Pass;
    return typeof p.access === 'string' && typeof p.refresh === 'string' && typeof p.expiresAt === 'number' ? p : null;
  } catch {
    return null;
  }
}

/** 출입증이 있으면 (만료됐으면 갱신해서) 돌려준다. 없으면 null. 갱신이 일시적으로 실패하면 예외(쿠키는 그대로) */
export async function currentPass(cookies: AstroCookies): Promise<Pass | null> {
  const pass = read(cookies);
  if (!pass) return null;
  if (pass.expiresAt - 60 > Date.now() / 1000) return pass;
  const fresh = await getBackend().refresh(pass);
  if (!fresh) {
    cookies.delete(PASS, { path: '/' });
    return null;
  }
  write(cookies, fresh);
  return fresh;
}

/** 출입증이 없으면 새 익명 출입증을 만든다. 익명 사용자는 비밀번호를 낼 때(POST)만 만든다:
 *  링크 미리보기 봇이나 그냥 열어 본 사람마다 사용자가 생기면 Supabase 익명 가입 한도에 걸린다 */
export async function ensurePass(cookies: AstroCookies): Promise<Pass> {
  const pass = (await currentPass(cookies)) ?? (await getBackend().signInAnonymously());
  write(cookies, pass);
  return pass;
}

export function readTextSize(cookies: AstroCookies): TextSize {
  return chosenTextSize(cookies) ?? 'base';
}

/** 사용자가 고른 적 있는 크기. 처음이면 undefined */
export function chosenTextSize(cookies: AstroCookies): TextSize | undefined {
  const v = cookies.get(SIZE)?.value;
  return v === 'base' || v === 'large' || v === 'xlarge' ? v : undefined;
}

export function writeTextSize(cookies: AstroCookies, size: TextSize) {
  cookies.set(SIZE, size, { path: '/', sameSite: 'lax', secure: import.meta.env.PROD, maxAge: MAX_AGE });
}

/** 고른 크기가 없으면 호칭으로 정한다: 할머니·할아버지는 '크게', 나머지는 '기본' */
export function sizeForName(name: string, chosen: TextSize | undefined): TextSize {
  return chosen ?? (/할머니|할아버지/.test(name) ? 'large' : 'base');
}
