import { SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL, SWEEPEA_BACKEND } from 'astro:env/server';
import { createMockBackend } from './mock';
import { createSupabaseBackend } from './supabase';
import type { Backend } from './types';

let cached: Backend | undefined;

export function getBackend(): Backend {
  if (cached) return cached;
  if (SWEEPEA_BACKEND === 'mock') {
    // 메모리 백엔드는 비밀번호가 코드에 박혀 있다. 운영 빌드에서 켜지면 바로 멈춘다
    if (import.meta.env.PROD) throw new Error('SWEEPEA_BACKEND=mock은 개발에서만 쓸 수 있다');
    return (cached = createMockBackend());
  }
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) throw new Error('SUPABASE_URL·SUPABASE_ANON_KEY가 없다');
  return (cached = createSupabaseBackend(SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY));
}

export type * from './types';
export { BackendError } from './supabase';
