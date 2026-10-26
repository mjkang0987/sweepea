// @ts-check
import { defineConfig, envField } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  // 출입증은 자체 쿠키 + Supabase로 관리한다. Astro 세션(KV)은 쓰지 않는다.
  session: false,
  // 아래 탭바·떠 있는 버튼을 가려서 끔
  devToolbar: { enabled: false },
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
      // 사진 주소 서명(HMAC). 운영에선 필수, 개발에선 없으면 프로세스마다 임시 값
      MEDIA_URL_SECRET: envField.string({ context: 'server', access: 'secret', optional: true }),
      // 부모 로그인에 켤 제공자(쉼표로). Supabase에서 켠 것만 적는다. 예: kakao,google,apple
      PARENT_PROVIDERS: envField.string({ context: 'server', access: 'secret', optional: true }),
      // 문자·카톡으로 보내는 공유 주소의 앞부분. 예: https://sweepea.co.kr
      SITE_ORIGIN: envField.string({ context: 'server', access: 'public', optional: true, url: true }),
      // mock: 개발·검사용 메모리 백엔드(운영 빌드에선 멈춤)
      SWEEPEA_BACKEND: envField.enum({ context: 'server', access: 'secret', values: ['supabase', 'mock'], default: 'supabase' }),
      // mock 전용: 저장 공간 레이어 확인용으로 사용량을 미리 더함(바이트)
      SWEEPEA_MOCK_USED_BYTES: envField.number({ context: 'server', access: 'secret', optional: true }),
    },
  },
});
