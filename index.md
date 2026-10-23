# index.md

스윗피(Sweetpea) 웹. 부모가 올린 아이 사진을 조부모·친척이 카톡 링크로 설치 없이 보는 가족 공유 앨범. 이 문서가 프로젝트 구조와 현재 상태의 기준이다. 작업 계획은 `plan.md`.

## 현재 상태

- 버전 0.1.0, 기본 설정 완료(`dev`). 실제 화면·데이터 연결은 아직 없다. 다음 이슈는 plan.md 참고.
- 첫 화면(`/`)은 심볼과 이름만 있는 임시 페이지. 클라이언트 JS 0KB.
- 로컬 Lighthouse(모바일, 기본 스로틀링): LCP 약 0.7초, CLS 0, 접근성 100점.

## 기술

| 영역 | 선택 |
| --- | --- |
| 웹 | Astro 7 서버 렌더링(`output: 'server'`), 필요한 곳만 바닐라 JS |
| 배포 | Cloudflare Workers (`@astrojs/cloudflare`, `wrangler.jsonc`) |
| 백엔드 (예정) | Supabase (Postgres·Auth·Edge Functions), 사진은 Cloudflare R2 |
| Node | 24 (`.nvmrc`). Astro 7은 22.23.4 이상 필요 |

## 구조

```
astro.config.mjs        Astro + Cloudflare 어댑터 (Images 바인딩·세션 KV 안 씀)
wrangler.jsonc          Worker 이름·호환 날짜
lighthouserc.json       성능 예산 (LCP 1.8초, CLS 0.05, JS 비압축 50KB, 접근성 100점)
.github/workflows/      perf.yml: 타입 검사 → 빌드 → 성능 예산 (PR, dev 푸시)
public/favicon.svg      심볼 (시스템 테마에 맞춰 색 바뀜)
src/styles/tokens.css   디자인 토큰 (색·글자·간격·모서리·터치). 원본은 디자인 시스템 '스윗피'
src/styles/base.css     문서 기본 스타일 (.sp-html, .sp-body, 포커스 링)
src/layouts/Base.astro  공통 HTML 뼈대 (lang=ko, theme-color)
src/pages/index.astro   임시 첫 화면
```

## 규칙

- CSS는 클래스·ID 선택자만. 태그 선택자 금지. 클래스 접두사 `sp-`.
- 테마는 기기 설정만 따른다. 색은 반드시 토큰 변수로.
- 네이티브 HTML 컨트롤 우선, 시맨틱 요소 우선, WCAG 2.2 AA.
- 성능 예산을 넘으면 머지하지 않는다.

## 명령

| 명령 | 하는 일 |
| --- | --- |
| `npm run dev` | 개발 서버 |
| `npm run check` | 타입 검사 |
| `npm run build` | 빌드 (`dist/`) |
| `npm run perf` | 빌드 결과로 Lighthouse CI 예산 검사 (Chrome 필요, `CHROME_PATH`로 지정 가능) |
