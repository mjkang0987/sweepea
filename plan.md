# plan.md

현재 진행 중인 작업과 앞으로의 계획. 기획서: [스위피 · 가족 공유 앨범 앱 기획서](https://claude.ai/artifact/MSiCj7dUjxWEbmwMba3Aei), 디자인: [스위피 메인 디자인](https://claude.ai/artifact/PWAPCX4B9x9UTW7CH75giU).

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

### 2. feature/rename-sweepea — 이름을 스위피(Sweepea)로 변경 (완료, dev 머지)

- 요구사항: 서비스 이름을 스윗피(Sweetpea)에서 **스위피(Sweepea)**로, 대표 도메인을 **sweepea.co.kr**(가비아, DNS는 Cloudflare)로 바꾼다
- 이유: "스윗피"는 2026년 OpenAI 이어버드 코드명 기사로 검색이 덮여 있고, 영어권에 같은 이름의 아기 기록 앱(Sweetpea - Baby Tracker)이 있다. sweetpea 도메인은 대부분 선점됨. Sweepea는 pea(콩)를 살려 심볼·콩이 마스코트를 그대로 쓴다
- 구현 방식: 화면 글자·문서·패키지·Worker 이름 교체. 디자인(색·심볼·마스코트)은 그대로
- 영향받는 파일: `README.md`, `index.md`, `plan.md`, `package.json`, `package-lock.json`, `wrangler.jsonc`, `src/pages/index.astro`, `src/layouts/Base.astro`, `src/styles/tokens.css`
- 예상 결과: 저장소 안에 옛 이름이 남지 않고, 빌드·성능 검사 통과
- 남은 일: 도메인 Active 후 Worker에 `sweepea.co.kr` 연결, 출시 전 키프리스 상표 확인(스위피·SWEEPEA, 9·42류)

### 3. feature/key-color-teal — 키컬러 틸 + 유리 버튼 토큰 (완료, dev 머지)

- 요구사항: 키컬러를 칙칙한 파인 그린(#2F7A5C)에서 틸(#0F766E, 다크 #2DD4BF)로. 타스·클립노트 보라와 겹치지 않게 초록 계열 유지
- 구현: `tokens.css` 색 교체, 사진 위 떠 있는 버튼용 유리 토큰(`--glass-tint`, `--glass-clear`, `--glass-edge`) 추가, 파비콘 색 교체
- 대비 확인: 흰 글자/틸 5.47:1, 검정 글자/밝은 틸 11.28:1, 유리 버튼은 흰 사진 위 최악 4.5:1 이상(불투명도 0.92)

### 4. feature/app-icon-kongi — 앱 아이콘·파비콘을 도트 콩이로 (완료, dev 머지)

- 요구사항: 앱 아이콘을 콩깍지 심볼에서 도트 콩이(3단계 떡잎)로. 근거: 구체적인 그림이 노인에게 더 빨리 인식되고(Zheng 2026), 가족·키즈 앱은 캐릭터 아이콘이 유리
- 구현: `public/favicon.svg`를 32×32 콩이 도트로 교체(라이트 연한 틸, 다크 짙은 틸 바탕). 홈 화면 아이콘(PNG·manifest)은 홈 화면 추가 이슈에서

## 다음 이슈 (기획서 '개발 이슈 분할' 순서)

저장소는 `sweepea` 하나에 웹과 `supabase/`를 같이 둔다(혼자 개발, DB와 화면 변경을 한 PR에서 검증). iOS·안드로이드는 나중에 `sweepea-ios`, `sweepea-android`.

1. 확인: 카톡 인앱 브라우저에서 출입증 쿠키 유지 (작은 테스트 페이지). 같이 확인: 카톡 → 외부 브라우저 자동 넘기기(`kakaotalk://web/openExternal`), `sms:` 문자 내용 미리 채우기(iOS·안드로이드), iOS 사파리 HEIC → JPEG 변환 시 촬영 시각 유지, iOS 26 사파리에서 공유 버튼 위치(홈 화면 추가 안내 문구 확정용)
2. supabase: 프로젝트 생성, 스키마·RLS·마이그레이션
3. supabase: 그룹 링크, 이름 선택 입장, 새 이름 pending·승인, 출입증·해제
4. supabase: 업로드 서명 URL, 완료 처리, 권한 필터링된 목록
5. supabase: 하트·댓글
6. cloudflare: 사진 전달 Worker (뷰어 전에)
7. web: 조부모 뷰어 (누구세요 → 넘겨 보기·모아 보기 → 크게 보기, 반응·직접 쓰기)
8. web: 화면 크기 설정 (3단계, 부모 원격 변경)
9. web: 부모 로그인(카카오·네이버·Google·Apple, 구현 안 된 건 비노출), 가족방·아이·구성원, 그룹 링크, 승인·기기 관리 (설정 > 가족)
10. web: 올리기 + 카톡 공유(카카오 JS SDK)
11. web: 아이 정보 카드 + 접종·검진 페이지
12. supabase·web: 부모 최근 반응·승인 목록 + iOS 홈 화면 추가 안내
13. supabase: 용량 집계, 5GB 상한
14. web: PC 화면 (모아 보기·크게 보기)

## 결정됨

- 이름: 스위피 / Sweepea (2026-10-23)
- 도메인: sweepea.co.kr 하나만. 다른 확장자 방어 등록은 하지 않음
- 앱 아이콘: 도트 콩이(3단계), 라이트 #E7F1F0 / 다크 #07221F 바탕 (2026-10-24)
- 키컬러: 틸 #0F766E / 다크 #2DD4BF, 떠 있는 버튼은 유리(주요는 색 유리, 보조는 투명 유리) (2026-10-24)
- 부모 로그인: 카카오 → 네이버 → Google → Apple. 시안엔 넷 다 두고, 구현 안 된 제공자는 버튼 비노출. Apple·Google은 공식 버튼·로고 규격 준수 (2026-10-24)

## 결정 필요

- 화면 문구 규칙(브랜드 리뷰 2026-10-24 반영): 실제 가족 호칭 사용, "카톡" 통일, 날짜 "~부터", 접종 일정은 출시 전 질병관리청 표준 일정과 대조

- Pretendard 글꼴: 동적 서브셋(CDN) vs 직접 서브셋 생성 — 첫 화면 성능 측정 후 결정
- 사진 저장소 R2 확정 여부 (기획서 권장 R2)
- 최소 지원 브라우저 (카톡 인앱 브라우저 기준)
