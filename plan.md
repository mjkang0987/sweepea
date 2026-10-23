# plan.md

현재 진행 중인 작업과 앞으로의 계획. 기획서: [스윗피 · 가족 공유 앨범 앱 기획서](https://claude.ai/artifact/MSiCj7dUjxWEbmwMba3Aei), 디자인: [스윗피 메인 디자인](https://claude.ai/artifact/PWAPCX4B9x9UTW7CH75giU).

## 진행 방식

- 이슈마다 `dev`에서 `feature/<이름>` 브랜치를 딴다.
- feature 안에서 작업 → 코드리뷰 → 개선 → 검증을 두 번 돌고 `dev`에 머지한다. `dev`에서 같은 사이클로 통합 확인 후 PR로 `main`에 올린다.
- 커밋은 한국어 + Conventional Commits 접두사, 작은 단위로.
- 성능 예산(LCP 1.8초, CLS 0.05, 첫 화면 JS 압축 후 50KB)을 넘으면 머지하지 않는다. CI는 비압축 50KB로 더 엄격하게 잰다(미리보기 서버가 압축을 안 함). 실제 JS가 붙어 이 기준이 과하면 압축 크기 측정으로 바꾼다.

## 지금 하는 일

### 1. feature/setup — 웹 기본 설정 (완료, dev 머지)

- 요구사항
  - Astro 서버 렌더링 + Cloudflare 어댑터로 빌드되는 빈 앱
  - 디자인 토큰을 CSS 변수로. 라이트/다크는 시스템 테마(`prefers-color-scheme`)만 따르고 앱 안 전환은 없다
  - 성능 예산 검사(Lighthouse CI)를 로컬과 GitHub Actions에서 돌린다
- 구현 방식
  - `src/styles/tokens.css`: 색·글자·간격 토큰. 태그 선택자 없이 `:root`와 클래스만
  - `src/layouts/Base.astro`: `lang="ko"`, `color-scheme`, 토큰 CSS
  - `src/pages/index.astro`: 임시 첫 화면(심볼 + 이름). 실제 화면은 뷰어 이슈에서
  - `lighthouserc.json` + `.github/workflows/perf.yml`
- 영향받는 파일: `package.json`, `astro.config.mjs`, `tsconfig.json`, `src/**`, `lighthouserc.json`, `.github/workflows/perf.yml`, `index.md`
- 예상 결과: `npm run build`가 통과하고, `npm run perf`가 예산 안에서 통과한다
- 범위 밖: Pretendard 글꼴 로딩(용량이 커서 서브셋 방식을 따로 정함), Supabase 연결

## 다음 이슈 (기획서 '개발 이슈 분할' 순서)

저장소는 `sweetpea` 하나에 웹과 `supabase/`를 같이 둔다(혼자 개발, DB와 화면 변경을 한 PR에서 검증). iOS·안드로이드는 나중에 `sweetpea-ios`, `sweetpea-android`.

1. 확인: 카톡 인앱 브라우저에서 출입증 쿠키 유지 (작은 테스트 페이지)
2. supabase: 프로젝트 생성, 스키마·RLS·마이그레이션
3. supabase: 그룹 링크, 이름 선택 입장, 새 이름 pending·승인, 출입증·해제
4. supabase: 업로드 서명 URL, 완료 처리, 권한 필터링된 목록
5. supabase: 하트·댓글
6. cloudflare: 사진 전달 Worker (뷰어 전에)
7. web: 조부모 뷰어 (누구세요 → 넘겨 보기·모아 보기 → 크게 보기, 반응·직접 쓰기)
8. web: 화면 크기 설정 (3단계, 부모 원격 변경)
9. web: 부모 로그인(Apple·카카오), 가족방·아이·구성원, 그룹 링크, 승인·기기 관리 (설정 > 가족)
10. web: 올리기 + 카톡 공유(카카오 JS SDK)
11. web: 아이 정보 카드 + 접종·검진 페이지
12. supabase·web: 부모 최근 반응·승인 목록 + iOS 홈 화면 추가 안내
13. supabase: 용량 집계, 5GB 상한
14. web: PC 화면 (모아 보기·크게 보기)

## 결정 필요

- Pretendard 글꼴: 동적 서브셋(CDN) vs 직접 서브셋 생성 — 첫 화면 성능 측정 후 결정
- 사진 저장소 R2 확정 여부 (기획서 권장 R2)
- 최소 지원 브라우저 (카톡 인앱 브라우저 기준)
