// Worker 진입점: 화면은 Astro 어댑터 그대로, 매일 정리 예약 작업만 더한다(wrangler.jsonc triggers.crons)
import { handle } from '@astrojs/cloudflare/handler';
import { createSupabaseBackend } from './lib/backend/supabase';
import { runCleanup } from './jobs/cleanup';

// 비밀 값은 wrangler secret으로 넣는다(타입은 wrangler.jsonc에 없어 여기서만 적는다)
type Secrets = { SUPABASE_URL?: string; SUPABASE_ANON_KEY?: string; SUPABASE_SERVICE_ROLE_KEY?: string };

export default {
  fetch: handle,
  async scheduled(_controller, env, ctx) {
    const s = env as Env & Secrets;
    if (!s.SUPABASE_URL || !s.SUPABASE_ANON_KEY || !s.SUPABASE_SERVICE_ROLE_KEY) {
      console.error('정리 작업: Supabase 비밀 값이 없다');
      return;
    }
    const backend = createSupabaseBackend(s.SUPABASE_URL, s.SUPABASE_ANON_KEY, s.SUPABASE_SERVICE_ROLE_KEY);
    ctx.waitUntil(runCleanup(backend, env.MEDIA).then((r) => console.log('정리 작업', JSON.stringify(r))));
  },
} satisfies ExportedHandler<Env>;
