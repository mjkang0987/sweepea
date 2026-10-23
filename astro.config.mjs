// @ts-check
import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  // 출입증은 자체 쿠키 + Supabase로 관리한다. Astro 세션(KV)은 쓰지 않는다.
  session: false,
  // 사진은 R2 + 사진 전달 Worker가 맡으므로 Cloudflare Images 바인딩은 쓰지 않는다.
  adapter: cloudflare({ imageService: 'passthrough' }),
});
