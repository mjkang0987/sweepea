// @ts-check
import { defineConfig, envField } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  // 출입증은 자체 쿠키 + Supabase로 관리한다. Astro 세션(KV)은 쓰지 않는다.
  session: false,
  // 비밀번호 POST는 같은 출처에서만(Astro 기본값이지만 꺼지지 않게 적어 둔다)
  security: { checkOrigin: true },
  // 사진은 R2 + 사진 전달 Worker가 맡으므로 Cloudflare Images 바인딩은 쓰지 않는다.
  adapter: cloudflare({ imageService: 'passthrough' }),
  env: {
    schema: {
      SUPABASE_URL: envField.string({ context: 'server', access: 'secret', optional: true }),
      SUPABASE_ANON_KEY: envField.string({ context: 'server', access: 'secret', optional: true }),
      // 올리기 완료 처리(sp_finish_upload)만 쓴다. 클라이언트로 절대 내보내지 않는다
      SUPABASE_SERVICE_ROLE_KEY: envField.string({ context: 'server', access: 'secret', optional: true }),
      // mock: 개발·검사용 메모리 백엔드(운영 빌드에선 멈춤)
      SWEEPEA_BACKEND: envField.enum({ context: 'server', access: 'secret', values: ['supabase', 'mock'], default: 'supabase' }),
    },
  },
});
