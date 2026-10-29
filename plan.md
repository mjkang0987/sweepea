# plan.md

현재 진행 중인 작업과 앞으로의 계획. 기획서: [스위피 · 가족 공유 앨범 앱 기획서](https://claude.ai/artifact/MSiCj7dUjxWEbmwMba3Aei), 디자인: [스위피 메인 디자인](https://claude.ai/artifact/PWAPCX4B9x9UTW7CH75giU).

## 새 세션 인계 (2026-10-29 기준, dev 0.5.5 배포됨)

새 세션은 이 절부터 읽는다. 자세한 기록은 아래 번호 이슈(86~96이 최근).

### 지금 상태

- dev = 0.5.5, dev에 푸시하면 운영 주소로 자동 배포(Workers Builds, 40~60초). 운영 주소 https://sweepea.co.kr (www는 대표 주소로 308, workers.dev도 살아 있음 `workers_dev: true` 필수). CI(perf: 타입 검사·빌드·Lighthouse)는 dev 푸시마다 → `gh run list --branch dev`
- main은 첫 커밋 그대로. PR #1(main ← dev, 제목은 0.2.0 시절)이 열려 있음 → main 머지는 사용자 확인 뒤, 제목·설명을 지금 버전으로 고친다
- 운영 Supabase(`aemzbelwyyweugxuqgoh`, 서울)에 마이그레이션 18개 모두 적용(18번째 `20261029000001_views.sql` 보신 기록, 2026-10-29 사용자 승인). 새 마이그레이션은 적용 전에 매번 사용자에게 묻는다. 적용 도구에 DROP이 들어가면 취소되므로 이름을 바꾼 새 함수로 만든다
- 디자인 캔버스: https://claude.ai/artifact/PWAPCX4B9x9UTW7CH75giU (v174). 화면 바꾸기 전에 반드시 여기부터 고친다. 보드 콩이 그림은 data URI로 넣는다(`/_blob`은 새 보드에서 깨짐)
- iOS 앱: 별도 저장소 `~/Desktop/git/sweepea-ios`(비공개 GitHub mjkang0987/sweepea-ios, 93). 1단계(디자인 토큰·버튼·토스트·레이어·칩, 부품 모아 보기)까지. 알려진 문제: 레이어가 탭바를 덮지 않음. 다음은 2단계(첫 화면·로그인·가족 입장)
- 이번 세션(2026-10-29)에 끝낸 것: 95 보신 기록(이름만, 0.5.0) · 96 주요 버튼 아래 고정·올리기 진행 칸(0.5.1) · 94 요금제 정함(무료+플러스 하나, 원본 보관·가족 플랜 없음) · 97 작은 사진 그대로(0.5.2) · 패밀리앨범 요금표 정리

### 다음 할 일 (순서대로)

1. **운영에서 보신 기록 확인**: 가족 기기로 사진을 열고(넘겨 보기는 가운데 1.5초) 엄빠 크게 보기 날짜 아래 "○○가 봤어요"가 뜨는지. 자동 검사는 mock에서만 돌렸음
2. **98 아이 나이별로 건너뛰기**(디자인 보드 먼저) → **경쟁력 기능 2: 조부모 음성 한마디**(94): 말로 남기고 받아 적은 글자도 같이 보임, 보내기 전 글자 확인. 받아 적기 방법(브라우저 음성 인식 vs 서버) 정하기 → plan.md에 계획 → 디자인 보드 먼저
3. 그다음 원본 보관(아직 없는 기능, 플러스) → 경쟁력 기능 3 액자 모드
4. **사용자 결정 남은 것**: 요금제 하나/둘(94 '스위피 플러스' 월 ₩5,900·연 ₩59,000 안), `/start`의 "콩이도 아이 나이에 맞춰 함께 자라요"는 지금 없는 기능(만들지 문구를 바꿀지), 사진 핀치 확대(웹은 브라우저 화면 전체 확대만 됨, 사진만 확대는 iOS 앱에서 자연스러움 — 웹에도 넣을지)
5. 사용자 쪽 할 일 안내만: 서치 콘솔(TXT 기록·sitemap), 카카오 공유 미리보기 디버거, 실기기(아이폰 사파리) 확인 — 아래 고정 막대가 사파리 아래 바 접힘·키보드 열림에서 괜찮은지(시뮬레이터 iOS 26에서는 확인함)
6. 기획서 문서(Claude Docs) 갱신: 자동 모드 분류기에 막혔음 → 사용자 허락 필요
7. 예전부터 남은 것: 옛 함수 `sp_media_comments` 지우기(DROP이라 사용자가 SQL 편집기에서 직접), `design-audit.md` 디자인 검수 남은 것, 아이폰 HDR 영상 색 확인
- 정함: 게스트 모드(혼자 쓰기) 없음(사용자 "게스트 서비스 막아야겠는데")

### 사용자 작업 규칙 (꼭 지킬 것)

- 답은 항상 한국어로, 영어·개발 용어 없이 쉬운 말로. 실수하면 "미안해, 내가 잘못했어"로 먼저 사과
- 순서: 원인을 찾아 먼저 말함 → plan.md에 계획 → 디자인 캔버스 먼저 고침 → 개발 → 코드리뷰·검증·기능검증 3회(사용자 2026-10-27 '꼭', 회차마다 따로 리뷰) → 디자인 보드와 실제 화면 나란히 대조, 차이 전부 맞춤 → 머지
- 디자인 시스템(토큰·컴포넌트) 꼭 지키기. CSS는 클래스·ID 선택자만, 네이티브 컨트롤·시맨틱 HTML·WCAG
- 브랜치는 origin/dev에서, dev에 `--no-ff` 머지, 머지마다 package.json·package-lock.json 버전 올림(`npm version x.y.z --no-git-tag-version`), 매번 푸시. 강제 푸시는 막혀 있음(커밋을 나눌 땐 푸시 전에)
- 커밋: 한국어 Conventional Commits, 작게. 끝에 빈 줄 하나 두고 Co-Authored-By·Claude-Session 줄(빈 줄이 없으면 제목에 붙어 버림)
- 비밀 값은 채팅·커밋에 넣지 않음(`.dev.vars.supabase`는 git 제외)

### 개발 도구 (`tools/`)

- `tools/dev.sh`: mock 백엔드 개발 서버(:4321). 환경의 node가 22.23.4보다 낮으면 Node 24를 `tools/.node`에 받아 씀. 백그라운드로 실행
- `tools/e2e/*.py`: 화면 흐름 검사(Python Playwright, 개발 서버 필요). 최근 것: instant(즉시 반영)·cdelete(한마디 지우기)·comments·toast·sheetios·photodel(사진 지우기 레이어)·motion. 실행: `cd tools/e2e && python3 instant.py` → 끝줄 `FAILS []`. 스크린샷은 `tools/shots/`(git 제외)
- 디자인 보드 만들기 `tools/design/*.py`, 보드 그려 보기 `tools/render/rdc.py`(`cd tools && python3 render/rdc.py out.png T_x.dc.html:light`, 파일은 `tools/canvas/project/`). `tools/canvas/`는 git 제외 → 새 세션에선 Artifact read(`path`)로 캔버스 파일(`project/*.dc.html`, `project/canvas.json`)을 받아 `tools/canvas/project/`에 두고, 올릴 때 Artifact publish `root`를 `tools/canvas`로
- 검사 명령: `npx astro check`, `npm run test:unit`(32개), DB 검사는 맥에서 `LC_ALL=C PG_BIN=/opt/homebrew/bin bash supabase/tests/run.sh`(의도한 거절 63개, 로캘이 ko면 initdb 실패)
- 개발 서버는 미리보기 도구 `sweepea-mock`(:4321, mock은 사진 없이 시작). 브랜치를 바꾸면 ENOENT로 죽으니 다시 켠다. 최근 검사: views.py(보신 기록)·bottombar.py(아래 고정·올리기 진행)·loadmore.py(인자: 임시 폴더)

## 진행 방식

- 이슈마다 `dev`에서 `feature/<이름>` 브랜치를 딴다.
- feature 안에서 작업 → 코드리뷰 → 개선 → 검증을 세 번 돌고(사용자 2026-10-27 기준) 디자인 대조까지 마친 뒤 `dev`에 머지한다. `dev`에서 같은 사이클로 통합 확인 후 PR로 `main`에 올린다.
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
  - `src/pages/index.astro`: 임시 첫 화면(심볼 + 이름). 실제 화면은 뷰어 이슈에서 → 91에서 소개 한 장으로
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

### 5. feature/db-schema — Supabase 스키마·RLS·입장 함수 (완료, dev 머지)

- 요구사항
  - 10월 24일 확정한 입장·보안 규칙을 DB에서 강제한다: 공유마다 짧은 링크(새 입장 72시간), 그룹별 4자리 비밀번호+힌트, 3번 틀리면 30초 쉬기, 10번 틀리면 승인 대기, 새 이름은 승인 대기 3일 뒤 만료, 이미 들어온 기기는 계속 열람
  - 그룹은 기본 꺼짐(가족방마다 기본 그룹 1개), 켜면 이름을 직접 정하고 그룹마다 "새 사진에 기본 포함"
  - 사진별 공개 그룹(여러 개), 아이 태그, 반응 5종(하트·최고·좋아·감동·반짝), 한마디
  - 올리기 권한 가족(배우자 등): 승인된 기기에만
  - 탈퇴 3일 유예(가족방에 삭제 예정 시각)
  - 권한 판정은 서버(RLS·보안 함수)에서만
- 구현 방식
  - `supabase/migrations/20261025000001_init.sql`: 테이블, 인덱스, RLS, 보안 함수(`sp_*`), 입장 RPC(`sp_enter`)
  - 부모는 Supabase Auth 사용자, 가족 기기는 Supabase 익명 사용자(기기 하나 = 익명 사용자 하나)
  - 비밀번호는 pgcrypto bcrypt 해시로만 저장
  - `supabase/tests/`: 로컬 Postgres 16에 `auth.uid()` 흉내 스키마를 깔고 마이그레이션 + 권한 시나리오 검사를 돌리는 스크립트(`npm run test:db`)
- 영향받는 파일: `supabase/**`, `package.json`(스크립트), `index.md`, `plan.md`
- 예상 결과: 로컬 검사에서 부모·가족·승인 대기·다른 그룹·만료 링크 시나리오가 모두 의도대로 통과
- 범위 밖: Supabase 프로젝트 생성·배포(계정 필요, 사용자 작업), 사진 업로드 서명 URL·R2(이슈 4·6), 인앱결제 영수증 검증, 추억(v1.x)
- 참고: 기획서의 '권한·공개 범위 규칙'·'데이터 모델' 표는 10월 24일 결정 이전 내용(고정 그룹, 7일 대기 등)이라 이 이슈 기준으로 함께 고친다
- 검토 두 번(별도 리뷰어) 반영: 빈 비밀번호 입장, 익명 사용자 갈아타기 무차별 대입, 그룹 번갈아 맞히기, 가족방 교차 참조, 이름 선점, 거절 기기 재입장 등. 검사 시나리오 40여 개, 의도된 거부 15건
- 남은 위험·후속
  - 4자리 비밀번호는 링크가 퍼지면 경보 한도 안에서 천천히(하루 30회) 맞힐 수 있다 → Supabase 연결 때 익명 로그인에 Cloudflare Turnstile을 켠다. 경보가 울리면 부모에게 알림(앱 출시 후)
  - 힌트는 디자인대로 입장 전에 보여 준다. "하린이 생일"처럼 비밀번호를 거의 알려 주는 힌트는 위험해서, 힌트 입력란에 안내 문구가 필요하다
  - 기기 하나는 가족방 하나에만 들어간다(할머니가 두 자녀 앨범을 한 폰으로 보는 경우는 나중에)
  - 부모 계정을 지우면 가족방에 주인이 없어진다 → 탈퇴 3일 유예 후 삭제 작업(예약 함수)에서 같이 처리

### 6. feature/entry-flow — 가족 입장 웹 화면 (완료, dev 머지)

- 요구사항
  - 공유 링크 `/i/<코드>` → 누구세요?(이름 고르기·직접 쓰기·글자 크기) → 가족 비밀번호 → 결과별 화면(들어감, 승인 기다림, 10번 틀림, 쉬는 중, 주소 기간 지남, 앨범 닫힘, 주소 없음, 내 가족 아님)
  - 출입증: Supabase 익명 세션을 httpOnly 쿠키(`sp_pass`)에 담는다. 이미 들어온 기기는 링크를 다시 열면 바로 앨범으로
  - 주소 없이 `sweepea.co.kr`로 오면 "가족에게 받은 주소로 들어와 주세요"
  - 글자 크기: 기본값 '기본', 할머니·할아버지 이름을 고르면 '크게'(쿠키 `sp_size`로 루트 글자 크기만 바꿈)
  - 클라이언트 JS 0KB(네이티브 폼 + 서버 렌더링). 카톡 인앱 브라우저·오래된 웹뷰에서도 동작
- 구현 방식
  - `src/lib/backend/`: 백엔드 인터페이스. `supabase.ts`(fetch로 Auth·RPC 호출, supabase-js 안 씀: 첫 화면 JS 예산), `mock.ts`(개발·검사용 메모리 구현, 운영에선 쓰지 못하게 막음)
  - `src/lib/pass.ts`: 출입증 쿠키 읽기·쓰기·토큰 갱신
  - 새 마이그레이션 `sp_me()`: 지금 기기 상태(승인 대기·차단·가족방 닫힘)와 이름
  - 화면: `src/pages/i/[code]/index.astro`, `src/pages/i/[code]/password.astro`, `src/pages/wait.astro`, `src/pages/album.astro`(다음 이슈 전까지 자리만), `src/pages/index.astro`(주소 없음), 공통 `src/styles/family.css`
  - 환경 변수(`astro:env`): `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SWEEPEA_BACKEND`(supabase·mock)
- 영향받는 파일: `astro.config.mjs`, `src/**`, `supabase/migrations/*_me.sql`, `supabase/tests/rls.sql`, `index.md`, `plan.md`
- 예상 결과: mock 백엔드로 브라우저에서 입장 흐름 전체가 동작하고, 빌드·성능 예산·DB 검사 통과
- 범위 밖: 앨범 화면(이슈 7), 부모 승인 화면(이슈 9), Turnstile(Supabase 연결 때), 실제 Supabase 연결 확인(프로젝트 생성 후)
- 결과: 검토 2회 반영, e2e·타입 검사·빌드 통과. 남은 위험: 부모가 기기를 거절했는데 액세스 토큰이 아직 살아 있으면 만료(최대 1시간)까지 오류 화면 → 실제 Supabase 연결 때 401 처리 확인

### 7. feature/multi-family — 한 기기로 여러 가족방 (완료, dev 머지)

- 요구사항
  - 할머니 한 명이 딸네(하린이네)·아들네(도윤이네)처럼 여러 가족방에 같은 기기로 들어갈 수 있다
  - 기기(익명 사용자) 하나가 가족방마다 따로 승인·차단·이름을 가진다. 한 가족방에서 차단돼도 다른 가족방은 그대로
  - 가족방끼리는 서로 안 보인다: 하린이네 엄마아빠는 할머니가 도윤이네에도 있다는 걸 모른다
  - 앨범은 기본으로 모든 가족방 사진을 섞어 보여 주고, 한 집만 골라 보기 가능(뷰어 이슈에서 화면 구현)
- 구현 방식
  - DB(아직 적용 전이라 기존 마이그레이션을 고침): `devices`의 unique를 `(auth_user_id, family_id)`로. 권한 함수는 가족방을 받는다(`sp_device_member(family)`, `sp_device_members()`, `sp_in_family`, `sp_media_member`)
  - `sp_enter`: 링크의 가족방 기준으로 기기를 찾고 만든다. `sp_me()`: `{families: [...]}`(마지막으로 들어가려던 곳이 끝)
  - `sp_entry_info`: 이 가족방에서의 내 상태(`me`)를 같이 돌려줘 이미 들어간 가족방이면 바로 앨범으로
  - `sp_create_share`: 가족방은 첫 그룹으로 정한다
  - 부모는 기기의 `auth_user_id`를 못 읽는다(열 권한). 두 집 부모가 맞춰 봐도 같은 기기인지 모르게. 부모 화면은 `select *` 대신 열을 적어야 한다
  - 웹: 누구세요 화면 이동 규칙을 '이 링크의 가족방' 기준으로. 글자 크기는 기기 하나에 하나
- 영향받는 파일: `supabase/migrations/`(새 마이그레이션), `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/pages/i/[code]/*`, `src/pages/album.astro`, `src/pages/wait.astro`, `index.md`, `plan.md`
- 예상 결과: 한 기기로 두 가족방에 각각 들어가고, 한쪽 차단·대기가 다른 쪽에 영향 없음. 가족방 사이 데이터가 섞이지 않음을 DB 검사로 확인
- 디자인: 앨범 위 가족방 고르기(모두 / 하린이네 / 도윤이네) 시안 추가 완료(캔버스 GrandMulti). 실제 구현은 JS 없이 링크(`?f=`) + `aria-current`, '모두'일 때 사진에 아이 이름표
- 결과: 검토 2회 반영. DB 검사(의도된 거부 17건), e2e(두 번째 가족방 입장 포함), 타입 검사·빌드 통과

### 8. feature/upload-api — 사진 올리기·목록 API (완료, dev 머지)

- 요구사항
  - 부모(또는 올리기 권한 가족)가 사진·영상을 올리면 R2에 저장되고, 볼 수 있는 가족에게 목록으로 보인다
  - 기획서 기준: 올리기 전에 기기에서 압축(사진 긴 변 2048 보기용 + 작은 썸네일, 영상은 포스터 이미지 함께). 원본 보관은 유료(나중)
  - 저장 키·용량·상태는 서버만 정한다(클라이언트가 크기를 속이지 못하게)
- 구현 방식
  - 업로드는 서명 URL 대신 **Worker를 거쳐 R2에 직접 넣는다**(R2 바인딩). R2 API 키·CORS 설정이 필요 없고, 크기를 Worker가 직접 잰다. 한 파일 100MB까지(Workers 요청 한도)
    1. 사진 행 만들기: 사용자 권한으로 `media` insert(기존 RLS가 올리기 권한 확인) → `uploading`
    2. `PUT /api/media/<id>/<view|thumb|poster>`: `sp_upload_target(id)`로 올린 사람·가족방 확인 → 형식(jpeg·webp·png·mp4·mov)·크기 확인 → R2 `<가족방>/<사진>/<종류>-<uuid>`(넣을 때마다 새 키, 응답으로 돌려줌)
    3. `POST /api/media/<id>/done` 본문 `{view, thumb, poster?}`(PUT이 준 키): 이 사진의 키인지·R2에 있는지 확인 → 서버 전용 `sp_finish_upload`(service_role)로 `ready`·키·용량 기록, 가족방 사용량 더하기
  - 목록: 새 SQL 없이 PostgREST로 `media` 읽기(RLS가 볼 수 있는 것만). `?family_id=`로 한 집만
  - 사진 행은 `sp_create_media`로만(직접 insert 막음). 올린 사람별 하루 안 끝낸 올리기 50개까지(넘으면 429)
  - 백엔드 계약에 올리기·목록 추가, mock도 구현(메모리 R2)
  - 환경: `wrangler.jsonc`에 R2 바인딩 `MEDIA`, 비밀 `SUPABASE_SERVICE_ROLE_KEY`
- 영향받는 파일: `supabase/migrations/`(새 마이그레이션), `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/pages/api/media/*`, `wrangler.jsonc`, `astro.config.mjs`, `index.md`, `plan.md`
- 예상 결과: 로컬에서 mock 백엔드 + 로컬 R2로 올리기 → 완료 → 목록까지 동작. 권한 없는 사람·남의 사진 id로 올리기 거부를 DB 검사·API 검사로 확인
- 범위 밖: 올리기 화면(이슈 10), 기기 압축 코드(이슈 10), 사진 보여 주는 Worker(이슈 6), 5GB 상한(이슈 13), 부모 로그인(이슈 9: 그 전까지 API 검사는 올리기 권한 가족 기기로)
- 사용자 작업: Cloudflare에서 R2 켜기(카드 등록), 버킷 `sweepea-media` 만들기
- 결과: 검토 2회 반영(가족 기기 올리기 버그, 덮어쓰기 경쟁, 인증 오류 500 등). DB 검사(의도된 거부 20건), 올리기 API e2e 20개, 입장 e2e, 타입 검사·빌드 통과. 남은 위험: 안 쓰인 파일·끝내지 않은 올리기 정리는 이슈 13, 실제 R2·Supabase에선 아직 안 돌려 봄

### 9. feature/photo-worker — 사진 전달 (완료, dev 머지)

- 요구사항
  - 볼 수 있는 사람만 사진·영상을 받는다. 앨범 칸마다 DB를 부르지 않게 빠르게
  - 영상은 이어 보기·넘겨 보기가 되게 범위 요청(Range) 지원
  - 올린 파일 형식을 브라우저가 다르게 해석하지 못하게(nosniff)
- 구현 방식
  - 앨범을 그리는 서버가 사진 목록(RLS로 볼 수 있는 것만)을 받고, 파일마다 **서명된 짧은 주소**(`/m/<키>?e=<만료>&s=<HMAC>`)를 만든다. 서명 키는 서버 비밀 `MEDIA_URL_SECRET`
  - `GET /m/<키>`: 서명·만료만 확인(DB 안 부름) → R2에서 꺼내 그대로 흘려 보냄. Range면 206
  - 만료는 1시간 단위로 맞춰 같은 시간대엔 같은 주소(브라우저 캐시가 먹게). 캐시는 `private`
  - 목록에 저장 키(view·thumb·poster)를 함께 받는다. 키를 알아도 서명 없이는 못 받는다
  - 앨범 자리 화면에 썸네일을 띄워 끝까지 확인(실제 뷰어는 이슈 7)
- 영향받는 파일: `src/lib/signed.ts`(새), `src/pages/m/[...key].ts`(새), `src/lib/backend/*`, `src/pages/album.astro`, `astro.config.mjs`, `index.md`, `plan.md`
- 예상 결과: 볼 수 있는 사람의 앨범에 썸네일이 보이고, 서명이 틀리거나 만료된 주소·다른 가족방 키는 거부. 영상 Range 206
- 범위 밖: Cloudflare 이미지 변환, 엣지 공유 캐시, 원본 내려받기(유료)
- 결과: 검토 2회 반영(범위 요청 경계, 412·304, `media` 읽기 열 제한: 부모 사용자 id·원본 키·용량은 RPC로만). DB 검사(의도된 거부 21건), 올리기·전달 e2e, 타입 검사·빌드 통과. 운영 배포 전 `MEDIA_URL_SECRET` 필요. 남은 위험: 막힌 기기도 받은 주소는 최대 2시간 열림, 실제 R2의 이상한 범위 처리는 미확인

### 10. feature/grand-viewer — 조부모 뷰어: 보기 (완료, dev 머지)

- 요구사항(캔버스 GrandHome·GrandList·GrandMulti·PhotoView·VideoView)
  - `/album`: 제목·사진 수, 집 고르기(여러 가족방일 때 모두/하린이네/도윤이네), 보기 탭(넘겨 보기·모아 보기)
  - 넘겨 보기: 큰 카드를 옆으로 밀어 넘김, "1 / 12", 카드를 누르면 크게 보기
  - 모아 보기: 날짜별 묶음, 칸 크기 −/+ (1·2·3·5칸), '모두'일 때 사진에 아이 이름표
  - 크게 보기 `/album/<id>`: 닫기, "3 / 12", 이전·다음, 사진은 화면에 맞춤, 영상은 재생
  - 클라이언트 JS 0KB 유지: 넘겨 보기는 CSS scroll-snap, 탭·집 고르기·칸 크기는 링크(`?v=`, `?f=`, `?z=`) + `aria-current`, 모아 보기 배치는 CSS columns
- 구현 방식: `src/pages/album/index.astro`·`[id].astro`, 공통 읽기는 `src/lib/album.ts`, 스타일은 `family.css`에 `.sp-a*`·`.sp-v*`. 사진 주소는 이슈 9의 서명 주소(넘겨 보기는 보기용, 모아 보기는 썸네일)
- 영향받는 파일: `src/pages/album.astro`, `src/pages/album/[id].astro`, `src/components/`, `src/styles/family.css`, `src/lib/backend/*`(목록에 아이 이름), `index.md`, `plan.md`
- 예상 결과: 실제 JPEG로 올린 사진이 세 보기에서 보이고, 키보드·스크린리더로 모두 조작 가능. 성능 예산 통과
- 결과: 검토 2회 반영(그림 설명 중복, 포커스 잘림, 다크 이름표 대비, 캐시 금지, 칸 크기 버튼 위치, 연도). 입장·올리기 e2e, 실제 JPEG로 화면 확인, 타입 검사·빌드 통과
- 넘겨 보기는 시안(GrandHome)대로 다시 맞춤: 290×360 가운데 카드, 양옆 카드는 기울고 흐림(CSS 스크롤 애니메이션, 지원 안 하는 브라우저는 평평하게), 카드 아래 "1 / 12 · 옆으로 밀거나 옆 사진을 누르세요", 탭은 흰 바탕+그림자
- 범위 밖(다음 이슈): 하트·한마디(이슈 5와 함께), 홈 화면에 두기 버튼, 머리말 '새 사진'·올린 사람(데이터 필요), 저장 버튼(가족방 '내려받기 허용' 설정), 생후 개월 표시(아이 생일·태그), 월별·연별 모아 보기, 영상 재생 막대 시안(A안)은 JS가 필요해 우선 브라우저 기본 재생 막대, 홈 화면에 두기 안내(이슈 12), 다음 쪽 넘기기(최근 200장)

### 11. feature/reactions — 하트·반응·한마디 (완료, dev 머지)

- 요구사항(캔버스 GrandHome·PhotoView)
  - 가족이 사진에 반응 5가지(하트·최고·좋아·감동·반짝)를 누르고 다시 누르면 취소. 카드·크게 보기에 하트 수와 내가 눌렀는지
  - "하린이에게 한마디"를 써서 보내기(200자). 가족 화면엔 목록 없이 "보냈어요"만(읽기는 부모 화면, 이슈 12)
  - 모아 보기 칸에 하트·한마디 배지
  - JS 없이: 버튼은 폼 POST → 같은 화면으로 돌아오기(PRG, 303). 넘겨 보기의 반응 줄은 카드마다 두고 가운데 카드 것만 보이게(CSS 스크롤 애니메이션, 지원 안 하면 카드 밑에 각각 보임)
- 구현 방식
  - DB(새 마이그레이션): `sp_react(사진, 종류, 켜기)`, `sp_comment(사진, 글)`(구성원별 하루 30개, 넘으면 429), `sp_reaction_counts(사진들)`(호출자 권한, RLS로 볼 수 있는 것만, 종류별 수·내가 눌렀는지·한마디 수)
  - 백엔드 계약에 react·comment·reactionCounts, mock 구현
  - 화면: `src/pages/album/[id].astro`(POST 처리), `src/pages/album/index.astro`, 반응 아이콘은 시안의 도트 SVG를 컴포넌트로
- 영향받는 파일: `supabase/migrations/`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/pages/album/*`, `src/components/`, `src/styles/family.css`, `index.md`, `plan.md`
- 예상 결과: 반응·취소·한마디가 DB 검사와 e2e로 확인되고, 남의 이름·다른 가족방·안 보이는 사진엔 반응 불가
- 범위 밖: 하트 떠오르는 효과(부모 화면), 한마디 고치기·지우기 화면, 부모 최근 반응(이슈 12)
- 결과: 검토 2회 반영(반응·한마디는 함수로만, 한마디 글은 부모·쓴 사람만, 승인 대기는 반응 불가, 이모지 한 번만 그리기, 옆 카드 반응 숨김, 지원 안 하는 브라우저는 반응 줄 숨김). DB 검사(의도된 거부 23건), 반응 e2e 13개, 타입 검사·빌드 통과
- 남은 일: 부모는 구성원 행이 없어 반응·한마디 함수가 막힘 → 부모 화면에서 반응하려면 함수에 부모 분기 필요(이슈 9·12). 키 작은 화면에서 반응 뒤 돌아올 때 반응 줄이 아래로 밀릴 수 있음(실기기 확인)

### 12. feature/parent-start — 부모 시작: 소개·로그인·처음 설정·앨범 (완료, dev 머지)

- 요구사항(캔버스 ParentIntro1~3·ParentLogin·ParentOnboard·ParentOnboard2·ParentEmpty·ParentHome)
  - 소개 3장(처음 한 번, 건너뛰기) → 로그인(카카오·네이버·Google·Apple, 구현 안 된 제공자는 버튼 숨김) → 처음 설정 1/2 아이(이름·생일·엄마/아빠) → 2/2 가족 비밀번호(숫자 4자리·힌트) → 앨범
  - 앨범: 사진이 없으면 "하린이 첫 사진을 올려 주세요", 있으면 월별 모아 보기. 아래 탭(앨범·설정), "사진 추가하기"(올리기 화면은 이슈 14)
  - 이미 설정한 부모는 로그인하면 바로 앨범, 로그인 안 했으면 소개/로그인으로
- 구현 방식
  - 로그인: Supabase Auth OAuth(PKCE). `/login/<제공자>` → Supabase 인증 → `/auth/callback`에서 코드 교환 → httpOnly 쿠키 `sp_parent`(가족 기기 출입증 `sp_pass`와 따로). 출입증 읽기·갱신은 `pass.ts`를 쿠키 이름만 바꿔 같이 쓴다
  - 켤 제공자는 환경 변수 `PARENT_PROVIDERS`(예: `kakao,google`). 네이버는 Supabase 기본 제공자가 아니라 따로 확인 필요(확인 전엔 숨김)
  - 개발용: mock 백엔드에서 `/login/dev`로 가짜 부모 로그인(운영 금지)
  - 처음 설정은 JS 없이 2단계 폼(1단계 값을 2단계에 숨은 칸으로), 마지막에 `sp_create_family`
  - 새 DB 함수 `sp_parent_home()`: 내 가족방·아이들·역할(없으면 null)
  - 부모 화면 스타일은 `parent.css`(.sp-p*), 높이 기준 52/40/56
- 영향받는 파일: `supabase/migrations/`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/lib/pass.ts`, `src/pages/{start,login,auth,setup,home}*`, `src/layouts/Parent.astro`, `src/styles/parent.css`, `astro.config.mjs`, `index.md`, `plan.md`
- 예상 결과: mock으로 소개 → 로그인 → 처음 설정 → 빈 앨범, 사진이 있으면 앨범까지 e2e 통과. 실제 OAuth는 Supabase 연결 때 확인
- 범위 밖: 설정 > 가족(승인·구성원·링크, 다음 이슈), 올리기 화면, 위 띠(승인 요청·접종 일정), 최근 반응, 아이 여러 명 전환, 이용약관·개인정보 처리방침 본문
- 결과: 검토 반영(없는 날짜·서울 날짜 기준, 비밀번호·힌트 검사, 로그아웃 때 Supabase 세션 끊기, 탭바·떠 있는 버튼 아래 여백, 오류 연결). 부모 e2e 16개·입장·올리기 e2e, 타입 검사·빌드 통과
- Supabase 연결 때 할 일: Additional Redirect URLs에 `https://sweepea.co.kr/auth/callback`(미리보기 주소도) 추가, 켤 제공자를 `PARENT_PROVIDERS`에. 네이버는 기본 제공자가 아니라 별도 확인

### 13. feature/family-settings — 설정 > 가족: 승인·링크 (완료, dev 머지)

- 요구사항(캔버스 Settings·Family·SendSetup)
  - 설정: '가족' 줄(승인 n · 그룹 n · 기기 n)과 로그아웃. 나머지 줄(아이·글자 크기·저장하기·계정·용량·플랜)은 다음 이슈
  - 설정 > 가족: 승인 기다리는 사람(새 이름: 거절 / '외가 가족으로 승인'), 새로 들어온 기기(비밀번호 10번 틀림·경보: 승인 / 내 가족 아님), 가족 그룹별 구성원과 '링크 만들기'
  - 링크를 만들면 주소와 함께 문자 보내기(`sms:`)·복사(길게 눌러 선택) 안내. 카톡 공유 버튼은 카카오 JS SDK가 필요해 올리기 이슈에서
  - 문자로 공유하기: 누구 폰인지 고르고(등록된 이름) 그 사람 전용 링크(한 번만 쓰는 문자 링크) + 미리 쓴 문자
- 구현 방식
  - 읽기: 부모 권한으로 PostgREST(`groups`, `members`, `devices` 정해진 열). 쓰기: 구성원 상태 PATCH(승인·거절), 기기 상태 PATCH(승인·내 가족 아님), 링크는 `sp_create_share`
  - JS 없이 폼 POST → 같은 화면으로(PRG). 승인·거절 같은 되돌리기 어려운 동작은 버튼 이름에 대상·결과를 적는다
  - 백엔드 계약: familyAdmin·setMemberStatus·setDeviceStatus·createShare, mock 구현(부모가 만든 링크로 가족이 들어오고 승인까지)
- 영향받는 파일: `src/lib/backend/*`, `src/pages/settings*`, `src/styles/parent.css`, `supabase/tests/rls.sql`(부모 PATCH 확인), `index.md`, `plan.md`
- 예상 결과: mock으로 부모가 링크를 만들고 → 가족이 새 이름으로 들어와 승인 대기 → 부모가 승인 → 가족 앨범이 열리는 e2e
- 범위 밖: 구성원 상세(올리기 허용·내보내기), 그룹 추가·이름·비밀번호 바꾸기, 기기 이름, 카톡 공유
- 결과: 검토 반영(승인 대기 기기 승인 때 같은 이름이면 그 사람으로 붙임·이름이 없어졌으면 막음, 거절하면 그 이름을 요청한 대기 기기도 막음, 한 사람용 문자 링크 72시간, 승인 대기인 것만 바꾸고 이미 처리·기간 지남은 안내, 거절·내 가족 아님은 한 번 더 확인, 만든 링크는 잠깐 쓰는 쿠키로(주소로 가짜 카드 금지), 공유 주소는 `SITE_ORIGIN`). 가족 e2e 11개와 기존 e2e 모두 통과
- 남은 일: 승인된 기기의 올리기 허용(구성원 상세 화면), 배포 때 `SITE_ORIGIN=https://sweepea.co.kr`

### 14. feature/upload-screen — 부모 올리기 화면 (완료, dev 머지)

- 요구사항(캔버스 ParentUpload)
  - 사진·영상 여러 장 고르기(기본 파일 고르기) → 미리보기(첫 장이 카톡 카드 대표, 다른 장을 눌러 바꾸기) → 아이·보여줄 그룹 고르기(체크박스, 그룹은 '기본 포함'이 미리 체크) → 크기 표시 → "올리고 카톡으로 보내기" / "보내지 않고 올리기만"
  - 기기에서 압축: 사진은 긴 변 2048 JPEG(보기용) + 긴 변 480(썸네일), 영상은 원본(100MB까지) + 첫 장면으로 포스터·썸네일
  - 찍은 날: JPEG EXIF 촬영 시각(시간대 정보 없으면 한국 시간), 없으면 파일 수정 시각
  - 올린 뒤 그 사진들만 담은 공유 링크를 만들어 공유 창(Web Share)으로 카톡 등에 보냄. 카카오 JS SDK 카드 공유는 카카오 앱 키를 받은 뒤
- 구현 방식
  - 부모 화면이라 JS 사용(가족 화면은 계속 0KB). `src/pages/upload.astro` + 페이지 스크립트, 순수 함수(EXIF 읽기·크기 계산)는 `src/lib/exif.ts`로 빼고 `node --test`로 검사
  - API가 부모 세션도 받게: `/api/media`는 부모 쿠키가 있으면 부모로, 없으면 가족 기기 출입증으로. 공유 링크는 새 `POST /api/shares`(그룹·사진)
  - 백엔드: createShare에 사진 목록, familyAdmin 그룹에 기본 포함 여부, mock은 부모 올리기 허용
- 영향받는 파일: `src/pages/upload.astro`, `src/pages/api/media/*`, `src/pages/api/shares.ts`, `src/lib/exif.ts`, `tests/`, `src/lib/backend/*`, `src/styles/parent.css`, `package.json`, `index.md`, `plan.md`
- 예상 결과: 브라우저에서 실제 JPEG를 골라 올리면 부모 앨범·가족 앨범에 보이고, 공유 링크로 들어온 가족에게 그 사진들이 보임(e2e). EXIF 날짜 단위 검사
- 범위 밖: 카카오 카드 공유(앱 키), 사진 정보 화면(찍은 날·그룹 바꾸기·지우기), 원본 보관(유료), 영상 압축, 페이지를 닫았다 연 뒤 이어 올리기
- 결과: 검토 반영(영상 이벤트 시간 제한, 실패 뒤 다시 누르면 이어 올리기·중복 없음, EXIF 이상한 파일 예외 방지, 처리 중 다시 고르기·두 번 누르기 막기, 대표 사진을 공유 링크 `cover_media_id`로 저장, 서버가 받는 영상 형식만 고르기, 캔버스 하나 돌려쓰기, 출입증을 가족방에 맞게 고르기, 초점·알림 영역). 올리기 화면 e2e 10개·이어 올리기 e2e·EXIF 단위 검사 5개·기존 e2e 통과
- 남은 위험: 아이폰 실기기(HEIC·영상 첫 장면·메모리)와 영상 업로드는 자동 검사 못 함(검사 브라우저가 H.264를 못 열음). 영상·EXIF 없는 사진의 찍은 날은 파일 시각

### 15. feature/settings-members — 설정: 구성원 상세·사진 저장하기·저장 용량 (완료, dev 머지)

- 요구사항(캔버스 MemberDetail·Settings·Storage)
  - 설정 > 가족 > 그룹의 사람을 누르면 구성원 상세: 이름·그룹·기기 수, **사진 올리기 허용**(체크박스, 이 사람의 승인된 기기에만), **내 가족 아님 · 내보내기**(한 번 더 확인, 기기도 막힘)
  - 설정 첫 화면: **가족도 사진 저장하기**(가족방 설정, 켜면 가족 크게 보기에 '저장' 버튼), **저장 용량**(사용량/5GB, 사진·영상 수)
  - 가족 크게 보기: 저장이 켜져 있으면 '저장' 링크(그 파일을 내려받기)
- 구현 방식
  - 읽기: 가족 관리 목록에 구성원별 기기(올리기 여부). 쓰기: 기기 `can_upload` PATCH(승인된 기기만), 구성원 거절은 기존 함수, 가족방 `download_allowed` PATCH
  - `sp_parent_home`에 용량·사진 수·저장 허용 추가, 가족 쪽 `sp_me`/`sp_entry_info`엔 저장 허용 여부
  - 폼 POST + PRG, 되돌릴 수 없는 동작은 확인 화면(설정 > 가족과 같은 방식)
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/lib/familyAdmin.ts`, `src/pages/settings/**`, `src/pages/album/[id].astro`, `src/pages/m/[...key].ts`(내려받기 이름), `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: mock으로 하린 아빠 올리기 허용 → 그 기기에서 올리기 가능, 내보내기 → 그 기기 막힘, 저장 켜기 → 할머니 화면에 저장 버튼 e2e
- 범위 밖: 아이·글자 크기·계정(다음 이슈), 가족 플랜·인앱결제
- 결과: 내려받기 이름은 `download` 속성으로 해결해 `/m` 변경 없음. 검토 두 번 반영: 올리기 허용은 그 사람의 모든 휴대폰이 켜져야 '켜짐'(새 휴대폰은 꺼진 채 들어옴), 내보내기 확인은 '내보낼까요?'(대기 중 이름은 '거절')·취소하면 구성원 화면, 내보낸 사람의 반응·한마디가 있으면 같은 이름 재사용으로 기록을 지우지 않고 그 이름은 막음, 스위치 설명 연결·기기 없을 때 이유 표시·고대비 표시, 저장 허용은 버튼만 보이게 하는 것(길게 눌러 저장은 못 막음)이라고 안내. DB 검사 추가(내보내면 기기 막힘·올리기 꺼짐, 기록 보존, 다른 가족방·가족 기기는 저장 허용 못 바꿈), e2e 10개·기존 e2e 통과
- 남은 위험: 실수로 내보낸 사람을 되살리거나 이름을 바꾸는 화면이 없음(그 이름은 계속 막힘). 영상 저장 이름은 늘 `.mp4`(아이폰 `.mov`도). 아이폰은 '파일'로 저장되고 카톡 인앱 브라우저는 `download`를 무시할 수 있음(실기기 확인 필요). `storage_used_bytes`는 늘기만 함(사진 지우기 때 빼기, 13번)

### 16. feature/settings-child-size-account — 설정: 아이·가족 화면 글자 크기·계정 (완료, dev 머지)

- 요구사항(캔버스 Settings·ChildSettings·ChildAdd·TextSize·Account)
  - 설정 첫 화면에 줄 추가: 아이(이름들), 가족 화면 글자 크기(지금 값), 계정(로그인 제공자·이름)
  - 아이: 목록(이름·생일·생후 개월) → 고치기(이름·생일), 아이 추가(이름·생일, 안내 "앨범 위에서 아이를 골라 볼 수 있어요")
  - 가족 화면 글자 크기: 관계에 맞춰(할머니·할아버지는 크게) / 모두 기본 / 모두 크게 / 모두 아주 크게 (라디오) + 외할머니 화면 미리보기. 처음 들어올 때 크기이고, 가족이 자기 화면에서 고른 크기가 먼저
  - 계정: 제공자 아이콘·이름·"카카오로 로그인 · 하린 엄마", 로그아웃
- 구현 방식
  - DB: `sp_parent_home`에 부모 이름·로그인 제공자(JWT `app_metadata.provider`)·글자 크기 설정 추가, `sp_entry_info`에 글자 크기 설정. 아이 추가·고치기와 글자 크기 설정은 기존 RLS·열 권한으로 PostgREST 직접(자기 가족방만)
  - 백엔드 계약: `addChild`, `updateChild`, `setTextSizeMode`
  - 입장(비밀번호 화면): 고른 크기 없으면 가족방 설정으로(관계에 맞춰면 지금처럼 호칭으로)
  - 화면은 폼 POST + PRG. 글자 크기 미리보기는 고른 라디오에 맞춰 CSS(`:has`)로 바뀜(JS 없음), 저장 버튼으로 반영
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/lib/pass.ts`, `src/pages/i/[code]/password.astro`, `src/pages/settings/index.astro`, `src/pages/settings/children/*`, `src/pages/settings/text-size.astro`, `src/pages/settings/account.astro`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: mock으로 아이 추가 → 설정·올리기 화면 아이 목록에 보임, 고치기 반영, 글자 크기 '모두 아주 크게' 저장 → 새로 들어온 가족 화면이 아주 크게(e2e). DB 검사: 다른 가족방 아이·글자 크기 못 바꿈, 가족 기기는 못 바꿈
- 결과: 부모 이름 대신 계정 화면은 "하린 엄마 · 카카오로 로그인"(설정에서 받은 부모 이름이 '엄마'·'아빠'라서). 로그아웃은 계정 화면으로 옮김. 검토 두 번 반영: 아이는 이름·생일만 넣고 고치게 열 권한 제한(지우기·순서는 아직 막음), 가족방당 아이 10명, 누구세요 화면부터 가족방 글자 크기, 미리 골라진 크기는 들어오기 전엔 저장 안 함, 아이 추가 다시 보내기 막기, 미리보기는 화면 읽기에서 제외. DB 검사(의도된 거부 29건)·생후 개월 단위 검사·e2e 16개·기존 e2e 통과
- 남은 위험: 아이 추가를 아주 빠르게 두 번 누르면 둘 다 들어갈 수 있음(10명 한도 안). 크기 쿠키는 기기 전체라, 다른 가족방에 이미 들어온 휴대폰은 그 크기를 유지. 네이버(직접 연결 제공자)는 제공자 이름이 '로그인'으로 보일 수 있음(실제 연결 뒤 확인)
- 범위 밖: 탈퇴하기·되살리기(다음 이슈, 캔버스 AccountDelete·AccountRestore), 접종·검진 일정 보기 체크(아이 정보 카드 이슈 11에서), 아이 지우기(사진 연결이 같이 지워져서 따로 확인 필요), 아이 사진, 가족 플랜, 구성원별 글자 크기 원격 변경

### 17. feature/account-delete — 탈퇴하기·되살리기 (완료, dev 머지)

- 요구사항(캔버스 AccountDelete·AccountDeleteSub·AccountDeleted·AccountRestore, 결정 2026-10-24 '탈퇴')
  - 계정 > 탈퇴하기 → 확인("정말 탈퇴할까요?", 3일 뒤 사진 N장·가족·아이 정보 삭제 안내, "모두 지워지는 것을 확인했어요" 체크해야 탈퇴하기)
  - 구독 중이면 탈퇴 대신 "구독 중이에요"(스토어에서 먼저 해지) 안내
  - 탈퇴하면 가족 화면은 바로 닫히고, 로그아웃 뒤 "그동안 고마웠어요"(지워지는 날짜, 처음으로)
  - 3일 안에 다시 로그인하면 "탈퇴 신청 중이에요" → 되살리기(그대로 돌아옴) / 그대로 탈퇴하기(로그아웃)
- 구현 방식
  - DB: `sp_request_delete()`(부모만, 구독 중이면 거부, `delete_after = now() + 3일`), `sp_restore_family()`(유예 중만 되돌림). 부모가 `delete_after`를 직접 못 고치게 열 권한에서 뺀다(아무 날짜나 넣어 바로 지워지는 걸 막음). 실제 삭제는 `sp_purge_deleted_families()`(service_role, 기한 지난 가족방 지우고 id 반환)
  - 부모 화면 진입(`loadParent`): 유예 중이면 `/restore`로. 확인 단계는 JS 없이 계정 화면의 확인 카드 + 기본 체크박스 `required`
  - 화면: `/settings/account`(탈퇴하기·확인), `/goodbye`(그동안 고마웠어요), `/restore`(되살리기)
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/lib/parent.ts`, `src/pages/settings/account.astro`, `src/pages/goodbye.astro`, `src/pages/restore.astro`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: mock으로 탈퇴 → 가족 앨범 닫힘·작별 화면, 다시 로그인 → 되살리기 → 앨범 다시 열림(e2e). DB 검사: 다른 부모·가족 기기는 탈퇴 못 함, 구독 중 거부, `delete_after` 직접 수정 불가, 기한 지난 가족방만 지워짐
- 범위 밖: 기한 지난 가족방을 실제로 지우는 예약 작업(Worker cron)과 R2 파일 삭제는 13번 정리 작업에서 같이(출시 전 필수), 부모 Auth 사용자 삭제, 가족 기기에 탈퇴 알림
- 결과: 검토 두 번 반영. 유예 중엔 부모도 올리기·공유를 멈춤(`sp_can_upload`), 지울 날이 지나면 부모에겐 가족방이 없는 것으로 보여 처음 설정으로 가고 그때 먼저 지움, 지운 가족방은 `r2_cleanup` 대기열에 남김, 구독 중이면 끝나는 날을 알려 주고 탈퇴 막음, 확인 체크를 안 하면 이유 안내, 작별 화면 날짜 검사. DB 검사(의도된 거부 35건)·탈퇴 e2e 15개·기존 e2e 통과
- **출시 전 필수(13번)**: 예약 작업 → 24번에서 만듦. 배포 뒤 실제로 도는지 확인 필요
- 남은 위험: 이미 받은 사진 주소는 닫힌 뒤에도 최대 2시간 열림. 구독 해지 여부는 모르고 끝나는 날까지 탈퇴를 막음(스토어 연동 때 갱신 상태 추가)

### 18. feature/restore-remaining — 탈퇴 신청 중 남은 시간 안내 (완료, dev 머지)

- 요구사항(사용자 요청 2026-10-26): "탈퇴 신청 중이에요" 화면에 지워지기까지 얼마나 남았는지 보여 준다
- 구현 방식: 지울 시각까지 남은 시간을 "2일 5시간 남았어요"(하루 미만 "5시간 남았어요", 1시간 미만 "곧 지워져요". 지울 날이 지나면 부모에겐 가족방이 없는 것으로 보여 이 화면은 안 뜬다)로. 화면을 연 시각 기준(JS 없음). 순수 함수 `remainingLabel`(`src/lib/age.ts`) + 단위 검사
- 영향받는 파일: `src/lib/age.ts`, `tests/age.test.ts`, `src/pages/restore.astro`, `index.md`, `plan.md`
- 예상 결과: 탈퇴 직후 다시 로그인하면 "2일 23시간 남았어요"(e2e), 경계값 단위 검사
- 결과: 빨간 굵은 글씨로 남은 시간, 아래에 지울 시각(예: 10월 29일 오전 1:46). 검토 반영(마지막 1시간·알 수 없는 값은 '곧 지워져요'). 단위 검사·탈퇴 e2e 통과. 화면을 연 시각 기준이라 열어 둔 채로는 줄지 않음

### 19. feature/group-settings — 그룹 관리: 그룹 목록·추가·상세·비밀번호 바꾸기·주소 다시 만들기 (완료, dev 머지)

- 요구사항(캔버스 GroupSettings·GroupDetail·PasswordChange)
  - 그룹 목록(`/settings/family/groups`): 그룹마다 이름·구성원 이름·인원·'기본 포함' 표시, 그룹 추가(10개까지)
  - 그룹 추가(`/settings/family/groups/new`): 이름·비밀번호 4자리·힌트·새 사진에 기본으로 포함
  - 그룹 상세(`/settings/family/groups/<id>`): 이름 바꾸기, 새 사진에 기본으로 포함(체크), 비밀번호(힌트)·바꾸기, 주소 카톡으로 보내기(기존 링크 만들기), 구성원(마지막으로 본 때·올리기·확인 기다림 남은 날), 주소 다시 만들기(예전 주소는 바로 막힘, 한 번 더 확인)
  - 비밀번호 바꾸기(`/settings/family/groups/<id>/password`): 새 비밀번호·힌트, "이미 들어온 기기는 그대로" 안내
  - 설정 > 가족에서 그룹 관리로 가는 줄
- 구현 방식
  - DB: `sp_add_group`에 10개 한도, `sp_reset_group_links(group)`(그 그룹이 들어간 공유 링크를 지워 예전 주소를 막음). 이름·기본 포함은 기존 열 권한으로 PATCH, 비밀번호는 기존 `sp_set_group_password`
  - 백엔드: `familyAdmin`에 그룹 힌트·기기 마지막으로 본 때, `addGroup`·`updateGroup`·`setGroupPassword`·`resetGroupLinks`
  - 폼 POST + PRG, 주소 다시 만들기는 설정 > 가족의 확인 카드·링크 카드 재사용
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/lib/familyAdmin.ts`, `src/pages/settings/family/index.astro`, `src/pages/settings/family/groups/*`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: mock으로 그룹 추가 → 목록·올리기 화면에 보임, 이름·기본 포함 바꾸기, 비밀번호 바꾸면 새 비밀번호로만 입장, 주소 다시 만들면 예전 링크는 없는 주소(e2e). DB 검사: 다른 가족방 그룹 못 바꿈, 11번째 그룹 거부, 다시 만들면 예전 코드 막힘
- 범위 밖: 그룹 지우기·순서 바꾸기, '홈 화면에 있음' 표시(설치 여부를 서버가 모름)
- 결과: 검토 두 번 반영. 주소 다시 만들기는 링크를 지우지 않고 막는다(`shares.revoked_at`, 그 링크로 들어와 승인 기다리는 사람은 링크 사진을 계속 봄), 탈퇴 유예 중엔 거절, 저장 실패 때 고른 값 유지. 비밀번호 검사(`pinError`)는 처음 설정과 같이 씀. DB 검사(의도된 거부 38건)·그룹 e2e 15개·기존 e2e 통과
- 남은 위험: 여러 그룹이 같이 들어간 링크는 한 그룹 주소를 다시 만들면 같이 막힘(안내 문구에 적음). 막힌 링크는 쌓이기만 함(정리 작업 13번에서)

### 20. feature/photo-info — 부모 사진 정보: 찍은 날·아이·보여줄 그룹 고치기, 사진 지우기 (완료, dev 머지)

- 요구사항(캔버스 ParentPhoto)
  - 부모 앨범에서 사진을 누르면 사진 정보(`/photo/<id>`): 큰 사진, 가장 최근 한마디(누가·무엇), 찍은 날(날짜), 아이(체크), 보여줄 그룹(체크, 하나 이상), "그룹을 빼면 그 가족 화면에서 바로 사라져요", 저장
  - 사진 지우기(한 번 더 확인): 사진·반응·한마디가 지워지고 저장 용량에서 빠짐
- 구현 방식
  - DB: `sp_update_media(사진, 찍은 날, 아이들, 그룹들)` 한 번에(부모 또는 올린 가족, 같은 가족방 아이·그룹만, 그룹 하나 이상), `sp_delete_media(사진)`(부모만, 용량 빼고 R2 정리 대기열에 넣고 행 삭제). R2 정리 대기열은 가족방 폴더뿐 아니라 사진 폴더도 담게 `r2_cleanup.prefix`로 바꾼다
  - 찍은 날은 날짜만 바꾸고 시각(서울)은 그대로, `taken_at_source = 'manual'`
  - 백엔드: `mediaInfo`, `updateMedia`, `deleteMedia`. 화면은 폼 POST + PRG, 지우기는 확인 카드
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/pages/home.astro`(칸을 링크로), `src/pages/photo/[id].astro`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: mock으로 사진 올림 → 사진 정보에서 그룹 빼기 → 그 그룹 가족 앨범에서 사라짐, 찍은 날 바꾸면 앨범 달이 바뀜, 지우면 앨범·용량에서 빠짐(e2e). DB 검사: 남의 사진·남의 가족방 그룹/아이 거부, 그룹 0개 거부, 가족 기기는 지우기 불가, 지우면 용량 감소·대기열
- 범위 밖: 올린 가족(배우자)이 자기 사진 고치는 화면(DB는 허용), 여러 장 한꺼번에 고치기. 영상은 기본 플레이어로 재생
- 결과: 검토 두 번 반영. 탈퇴 유예 중엔 고치기·지우기 거절(화면은 원래 되살리기로 감), 다 올라간 사진만 지우기, 오늘로 바꿔 미래 시각이 되면 지금으로, 오류를 해당 칸에 연결. DB 검사(의도된 거부 44건)·사진 정보 e2e 10개·기존 e2e 통과
- 남은 위험: 그룹을 빼거나 지워도 이미 받은 사진 주소는 최대 2시간 열림. PostgREST 연결 표 불러오기(`media_groups(...)`)는 실제 Supabase에서 확인 필요(확인 필요 목록)

### 21. feature/parent-reactions — 부모 최근 반응 (완료, dev 머지)

- 요구사항(캔버스 ParentReactions, 결정 '부모 알림은 앱 전까지 없음, 열면 보임')
  - 부모 앨범 위에 '최근 반응'(새 반응 수) → `/reactions`: 가족이 남긴 하트·반응·한마디(사진 썸네일, "외할머니 하트를 보냈어요", "외할머니 "…"", 10분 전·1시간 전·어제), 승인 기다리는 사람("큰이모 외가 앨범에 들어오려고 해요 · 확인 ›")
  - 열면 '새 반응'이 읽음으로
- 구현 방식
  - DB: `parents.activity_seen_at`, `sp_parent_activity()`(최근 30일, 50개, 승인된 가족의 반응·한마디만, 지운 한마디 제외) + `sp_mark_activity_seen()`, `sp_parent_home`에 새 반응 수
  - 화면은 서버에서 그리고 JS 없음. 사진을 누르면 사진 정보로, 승인 대기는 설정 > 가족으로
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/lib/age.ts`(몇 분 전), `src/pages/home.astro`, `src/pages/reactions.astro`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: mock으로 가족이 하트·한마디 → 부모 앨범에 '새 반응 2', 최근 반응 목록, 열고 나면 0(e2e). DB 검사: 다른 가족방 반응 안 보임, 내보낸 사람 반응 빠짐, 가족 기기는 함수 불가
- 범위 밖: 앱 알림, 한마디에 답하기
- 결과: 검토 두 번 반영. 읽음 표시는 목록을 읽은 시각까지만(그 사이 온 반응은 다음에 새 반응), 새 반응 수와 목록 규칙 맞춤(30일·다 올라간 사진), 시각 색인, 사진이 없어도 최근 반응 줄. DB 검사·최근 반응 e2e 7개·기존 e2e 통과
- 남은 위험: 하트를 껐다 켜면 새 반응으로 다시 올라옴. 배지는 50개 넘게 셀 수 있음(목록은 50개). 반응 저장 시각이 트랜잭션 시작 시각이라 아주 짧은 순간 겹치면 새 반응 표시를 놓칠 수 있음

### 22. feature/health — 접종·검진 일정 (완료, dev 머지)

- 요구사항(캔버스 Health·ChildSettings, 기획 이슈 11 일부)
  - 부모 앨범 위 아이별 줄(다음 일정) → `/health/<아이 id>`: 아이·생후 개월, 다가오는 일정(접종/검진, 권장 시기, 지금 가능·시기 지남·N월 N일부터), 완료(체크한 날), "국가 권장 시기 기준. 실제 기록은 질병관리청 예방접종도우미에서"
  - 체크하면 완료한 날(오늘)이 기록됨. 부모만 보고(가족 화면엔 안 보임)
  - 설정 > 아이: "앨범에 접종·검진 일정 보기"(끄면 앨범 위 줄이 사라짐)
- 일정 데이터(2026-10-26 확인): 국가예방접종 표준 일정(질병관리청 표, 동대문구 보건소 게시 2026-01-05 수정본)과 영유아 건강검진 1~8차(생후 14~35일, 4~6, 9~12, 18~24, 30~36, 42~48, 54~60, 66~71개월). 질병관리청 원문 사이트는 자동으로 못 읽어 보건소 게시본으로 확인 → 확인 필요 목록
  - 넣지 않는 것: 인플루엔자(매년), HPV(성별 정보 없음), 구강검진(보건소마다 시기 표기가 달라 확인 필요), 결핵 경피용·유료 백신
- 구현 방식
  - `src/lib/health.ts`: 일정 표(키·종류·이름·권장 시기 글·시작/끝 개월) + 생일로 날짜 계산(달력 개월) + 상태. 단위 검사
  - DB: `health_done(child_id, item_key, done_on)`(부모만, RLS), 아이 `show_health` 열 권한
  - 화면은 폼 하나(체크박스 + 저장), JS 없음
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/health.ts`, `tests/health.test.ts`, `src/lib/backend/*`, `src/pages/health/[id].astro`, `src/pages/home.astro`, `src/pages/settings/children/index.astro`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: 13개월 아이로 일정 상태가 맞게 보이고, 체크·저장하면 완료로, 끄면 앨범 위 줄이 사라짐(e2e). 날짜 계산 단위 검사. DB 검사: 다른 가족방·가족 기기는 못 읽고 못 씀
- 범위 밖: 접종 알림, 예방접종도우미 연동, 아이 정보 카드(사진·키·몸무게)
- 결과: 검토 두 번 반영. 일본뇌염 차수 나눔(1·2차 12~23개월, 3차·생백신 2차 24~35개월), 로타 접종 끝 시기(1차 14주 6일, 2·3차 8개월 전), A형간염 2차는 1차를 체크한 날 6개월 뒤부터, 처음 쓰는 부모를 위해 오래된 항목은 '지난 일정'으로 접기, 화면을 그릴 때 체크돼 있던 것만 풀기, 일정 오류가 나도 앨범은 보이기. 단위 검사 14개·DB 검사·e2e 5개·기존 e2e 통과
- 남은 위험: 일정 데이터는 보건소 게시본 기준(원문 대조는 확인 필요). 체크를 풀면 완료한 날이 지워짐

### 23. feature/install-guide — 홈 화면에 두기 (완료, dev 머지)

- 요구사항(캔버스 GrandInstall·InstallGuide, 결정 '가족 화면 홈 화면에 두기 버튼은 채운 버튼')
  - 가족 앨범 아래에 "홈 화면에 두세요" 안내(아이폰: 공유 → 홈 화면에 추가 → 추가 / 안드로이드: 메뉴 ⋮ → 홈 화면에 추가 → 추가), 알겠어요·다음에 할게요
  - 카톡 안에서 열렸으면: "카톡 안에서는 둘 수 없어요" + 엄마아빠에게 부탁하기(부모 최근 반응에 "외할머니가 홈 화면에 두기를 부탁했어요 → 문자로 공유하기")
  - 홈 화면 아이콘으로 열면(standalone) 안내를 보이지 않음
  - 웹 앱 매니페스트·아이콘(PNG 180·192·512, 마스커블)으로 홈 화면 아이콘이 콩이로 보이게. `/`는 부모면 앨범(/home), 가족이면 앨범(/album)
- 구현 방식
  - 기기 종류는 서버에서 User-Agent로 고름(아이폰·안드로이드·카톡·그 밖). 이미 홈 화면에서 연 경우는 CSS `@media (display-mode: standalone)`로 숨김(JS 없음)
  - 알겠어요·다음에 할게요는 폼 POST로 쿠키(다음에: 7일, 알겠어요: 1년)
  - DB: `members.install_help_at`, `sp_request_install_help()`(가족 기기 본인만), 부모 최근 반응에 7일 동안 표시
- 영향받는 파일: `public/manifest.webmanifest`, `public/icons/*`, `src/layouts/Base.astro`, `src/pages/index.astro`, `src/pages/album/index.astro`, `src/components/InstallGuide.astro`, `src/lib/install.ts`, `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/lib/backend/*`, `src/pages/reactions.astro`, `src/styles/family.css`, `index.md`, `plan.md`
- 예상 결과: 아이폰·안드로이드·카톡 UA마다 맞는 안내(e2e), 다음에 할게요 누르면 숨김, 부탁하기 → 부모 최근 반응에 보임. 성능 예산(가족 화면 JS 0KB) 유지
- 결과: 검토 두 번 반영. 안내는 떠 있는 판 대신 앨범 위 판(앨범·초점을 가리지 않게), 앱 안 브라우저(카톡·네이버·라인·인스타·페이스북·밴드·이름 모를 웹뷰)는 부탁하기, 단계를 모르는 브라우저(아이폰 크롬·웨일, 삼성 인터넷)는 안내 안 함, 부탁은 승인된 가족만. 단위 검사·DB 검사·e2e 10개·기존 e2e 통과. 가족 화면 JS 0KB 유지
- 범위 밖: 카톡에서 외부 브라우저로 넘기기(`kakaotalk://web/openExternal`은 실기기 확인 필요, 넘어가면 출입증 쿠키가 없어 다시 들어와야 함 → 확인 필요), 설치 여부 서버 기록

### 24. feature/cleanup-jobs — 정리 예약 작업·5GB 상한 (완료, dev 머지)

- 요구사항(이슈 13, 결정 '탈퇴 3일 뒤 삭제', 저장 용량 5GB)
  - 매일 한 번(서울 새벽 3시대) 예약 작업: 탈퇴 기한 지난 가족방 지우기, 하루 지난 '올리는 중' 사진 지우기, R2 정리 대기열의 폴더 파일 지우기
  - 올리기를 끝낼 때 같은 사진 폴더에 남은 예전 파일(PUT마다 새 키) 바로 지우기
  - 무료 가족방은 저장 용량 5GB가 차면 새로 올리기만 멈춤(가족은 계속 봄), 올리기 화면에 안내
- 구현 방식
  - Worker 진입점을 `src/worker.ts`로(어댑터의 `@astrojs/cloudflare/handler`로 화면은 그대로, `scheduled`만 추가). `wrangler.jsonc`에 `main`·`triggers.crons`
  - DB(service_role만): `sp_cleanup_stale_uploads()`, `sp_r2_cleanup_take(개수)`, `sp_r2_cleanup_done(폴더)`. `sp_create_media`에 5GB 상한(PT507 → HTTP 507)
  - 작업 본체는 `src/jobs/cleanup.ts`(백엔드·버킷을 받아서), 가짜 버킷으로 단위 검사
- 영향받는 파일: `supabase/migrations/*`, `supabase/tests/rls.sql`, `src/worker.ts`, `src/jobs/cleanup.ts`, `tests/cleanup.test.ts`, `wrangler.jsonc`, `worker-configuration.d.ts`, `src/lib/backend/*`, `src/lib/media.ts`, `src/pages/api/media/[id]/done.ts`, `src/pages/upload.astro`, `index.md`, `plan.md`
- 예상 결과: 단위 검사(대기열 폴더의 파일을 지우고 끝 표시, 실패한 폴더는 남김), DB 검사(기한·하루 기준, service_role만, 5GB 거절), 빌드 결과에 scheduled 핸들러
- 범위 밖: 가족 플랜(유료) 상한, 정리 결과 알림, 실제 Cloudflare 예약 실행 확인(배포 뒤 → 확인 필요)
- 결과: 검토 두 번 반영. 예약 작업은 끝까지 기다리고 실패가 있으면 예약 기록에 실패로 남김, 앞 단계가 실패해도 R2 정리는 계속, 외부 호출 45개 안에서 쪽마다 멈추고 다 못 지운 폴더는 대기열에 남겨 다음 날 이어서. 미리보기 서버에서 scheduled 핸들러 동작 확인(비밀 값 없음 로그). 단위 검사 6개·DB 검사(의도된 거부 48건)·기존 e2e 통과

### 25. feature/pc-layout — PC 화면 (완료, dev 머지)

- 요구사항(캔버스 GrandListPC·PhotoViewPC·ParentHomePC·ParentUploadPC, 기획 이슈 14)
  - 넓은 화면(64rem 이상)에서 가족 앨범·크게 보기는 넓게(모아 보기 4·6·8칸), 부모 앨범은 넓게 + 메뉴가 위로(6칸), 올리기는 왼쪽 사진·오른쪽 아이·그룹·보내기 두 칸, 사진을 끌어다 놓아 고르기
- 구현 방식: CSS 미디어 쿼리만(가족 화면 JS 0KB 유지). 넓힐 화면만 레이아웃에 `wide` 표시. 올리기 끌어다 놓기는 부모 화면이라 작은 스크립트(파일 입력에 넘김)
- 영향받는 파일: `src/layouts/Family.astro`, `src/layouts/Parent.astro`, `src/pages/album/*.astro`, `src/pages/home.astro`, `src/pages/upload.astro`, `src/styles/family.css`, `src/styles/parent.css`, `index.md`, `plan.md`
- 예상 결과: 1280px에서 화면이 넓게 쓰이고, 390px은 그대로(e2e 스크린샷·기존 e2e). 끌어다 놓기로 사진이 골라짐(e2e)
- 범위 밖: 부모 앨범 아이별 거르기(시안의 전체·하린·도윤), 크게 보기 양옆 화살표(이전·다음 링크는 아래 그대로), 마우스 오버 효과
- 결과: 검토 두 번 반영. 가족은 모아 보기·크게 보기만 넓게(넘겨 보기는 좁게 그대로), PC에서 다 올린 뒤 올리기 칸 숨김, 위 메뉴 밑 포커스 가림 막기, 칸 밖에 떨어뜨려도 화면 유지. PC e2e 10개·기존 e2e 통과

### 26. feature/swipe-wide — 넓은 화면 넘겨 보기 (완료, dev 머지)

- 요구사항(사용자 피드백 2026-10-26 "넘겨보기 UI 왜저래"): 화면이 가운데 칸보다 넓으면(태블릿·PC) 넘겨 보기 줄이 가운데 칸 끝에서 잘려 옆 카드가 뚝 끊겨 보인다. 휴대폰처럼 화면 끝까지 이어지게
- 구현 방식: 처음엔 줄을 화면 끝까지 펼쳤는데 카드 크기·겹침 애니메이션(view-timeline)이 줄 너비 기준이라 옆 카드가 가운데를 덮어서 되돌림. 대신 가운데 칸(32rem)보다 넓은 화면에서 줄 양끝 1.25rem을 흐리게(mask). CSS만
- 영향받는 파일: `src/styles/family.css`, `src/styles/base.css`(필요하면), `index.md`, `plan.md`
- 예상 결과: 1280px에서 옆 카드가 칸 끝에서 부드럽게 흐려지고 반응 버튼은 그대로, 390px은 그대로(스크린샷·기존 e2e)
- 결과: 검토 두 번(기준 폭을 칸 너비에 맞춤). 반응 e2e 통과

### 27. feature/group-pw-dots — 그룹 비밀번호 화면 정리 (완료, dev 머지)

- 요구사항(사용자 피드백 2026-10-26): ① 부모 그룹 상세 "비밀번호 ••••"의 점이 무슨 뜻인지 모르겠다 → 삭제 ② 비밀번호 칸이 시안은 왼쪽 정렬인데 코드는 가운데 정렬 → 한때 왼쪽으로 맞췄다가, 사용자 결정("비밀번호는 다 가운데정렬")으로 가운데 정렬 유지
- 구현 방식: 줄 제목을 "비밀번호"만 남김. 부모·조부모 비밀번호 칸 모두 가운데 정렬 그대로(왼쪽 정렬 커밋은 되돌림). 시안 보드의 부모 비밀번호 칸 3곳은 가운데로 고쳐야 함
- 영향받는 파일: `src/pages/settings/family/groups/[id]/index.astro`, `src/styles/parent.css`, `plan.md`
- 예상 결과: 그룹 상세에 점이 안 보이고, 비밀번호 칸은 모두 가운데 정렬(스크린샷·groups e2e)

### 28. feature/activity-split — 최근 반응과 들어오기 요청 나누기

- 요구사항(사용자 피드백 2026-10-26 "최근반응 반응이랑 진입요청이랑 분리해서 노출"): 최근 반응 화면에 반응·한마디만. 들어오려는 사람(승인 대기)과 홈 화면에 두기 부탁은 앨범 위에 따로 띠로 보인다(시안 부모 앨범의 승인 요청·설치 부탁 띠)
- 구현 방식
  - `/reactions`: '도와줄 사람'·'확인할 사람' 칸을 뺌. familyAdmin 호출도 뺌
  - `/home`: familyAdmin을 목록과 같이 불러(실패하면 띠만 안 보임) 띠 두 개. ① 확인할 사람(대기 구성원+새 휴대폰): 한 명이면 "{이름}이 {그룹} 앨범에 들어오려고 해요", 새 휴대폰만이면 "새 휴대폰 {N}대가 들어오려고 해요", 여럿이면 "{N}명이 들어오려고 해요" → `/settings/family` "확인 ›" ② 홈 화면에 두기 부탁(7일 안): "{이름}이 홈 화면에 두기를 부탁했어요"(여럿이면 "외 N명") → `/settings/family/sms` "문자 ›"
  - 띠 모양: pea-tint 바탕, pea-deep 글자, 56px, radius 14px(시안). 도트 이모지는 범위 밖
- 영향받는 파일: `src/pages/reactions.astro`, `src/pages/home.astro`, `src/styles/parent.css`, `plan.md`, 작업 폴더 e2e(reactions·install)
- 예상 결과: 최근 반응엔 반응만, 앨범 위 띠에서 승인·부탁으로 감(e2e)
- 결과: 검토 반영(이/가 조사, 새 휴대폰만 기다릴 때 문구). reactions·install·parent·members·health e2e 통과

### 29. feature/video-player — 가족 크게 보기(사진·영상) 새 배치 (디자인 버전 96)

- 요구사항(사용자 2026-10-26, 디자인 먼저 고친 뒤 적용)
  - 크게 보기는 화면 고정 겹침 배치: 사진·영상이 위 메뉴 뒤까지 화면을 채우고, 위 메뉴(닫기·n/N·저장)와 아래 판이 그 위에 겹친다
  - 위 메뉴·아래 판은 반투명, 판 안 버튼·칸은 판 배경보다 진하게: 라이트 판 흰 75%·버튼 85%·입력칸 92%, 다크 판 검정 65%·버튼 회색 85%·입력칸 검정 70%(처음 50/72/86·42/72/60에서 글자 대비 때문에 올림, 사용자 확인 2026-10-26), 배경 흐림 20px. 투명도 줄이기 설정이면 꽉 채움
  - 아래 판: (영상만) 재생 막대(6px 캡슐·28px 손잡이·44px 누르는 영역, 시간 양끝)·소리 버튼 → 날짜·하트 → 반응 5개 → 한마디 칸
  - 반응 버튼은 이모지만(글자 삭제, 이모지 40px, 버튼 높이 60px). 화면 읽기용 이름은 그대로. 넘겨 보기도 같이
  - 넘겨 보기의 "직접 쓰기" 버튼 대신 한마디 칸을 바로 보인다
  - 영상: 가운데 72px 재생 버튼. 재생하면 위 메뉴·가운데 버튼·‹ ›·날짜·반응·한마디가 숨고, 맨 아래 반투명 줄에 재생 막대(손잡이)·시간·소리 버튼만 남음(재생 중에도 끌어서 옮기기). 재생 중 화면을 누르면 일시정지 + 메뉴 다시 보임. 자동 숨김·작은 안내 글자 없음(어르신이 못 봄). 소리는 켜진 채로 시작. 시간 글자는 진한 글자색(반투명 위 대비)
  - 넘기기: 옆으로 밀면 이전·다음. 한 번 누르는 대체 수단으로 양옆 가운데 48px 반투명 ‹ › 버튼(WCAG 2.5.1). 영상 재생 중엔 메뉴와 같이 숨음. 맨 아래 이전·다음 버튼은 삭제
- 결정: 크게 보기 화면에만 작은 스크립트 허용(사용자 "1번으로"). 모아 보기·넘겨 보기 등 다른 가족 화면은 0KB 유지
- 구현 방식
  - `album/[id].astro`: `sp-v` 겹침 배치(position fixed 무대, 미디어 `object-fit: contain`(잘리지 않게)). ‹ ›는 진짜 링크(`rel=prev/next`)라 스크립트 없이도 넘어감
  - 영상: HTML엔 `controls`. 스크립트가 돌면 `controls`를 빼고 직접 만든 재생 버튼·막대·소리 버튼을 보임(스크립트 실패 시 기본 막대로 볼 수 있음). 재생 막대는 네이티브 `<input type="range">`, 재생·소리는 `<button>` + aria-label 바꿈. 길이는 `duration_sec` 있으면 서버에서 먼저 씀
  - 밀기: pointer 이벤트로 가로 이동이 세로보다 크고 일정 거리 넘으면 ‹ › 링크 주소로 이동. 재생 막대·입력칸·버튼에서 시작한 터치는 제외
  - 스크립트는 페이지 안 작은 모듈 하나(목표 2KB 이하, 압축 전)
- 영향받는 파일: `src/pages/album/[id].astro`, `src/components/ReactRow.astro`, `src/pages/album/index.astro`(직접 쓰기→한마디 칸), `src/styles/family.css`, `plan.md`, `index.md`(가족 화면 JS 예외)
- 예상 결과(390·1280px, e2e): 디자인과 같은 배치, 재생→메뉴 숨김·진행 선, 화면 누르면 일시정지·메뉴, 막대 끌기, 소리 켜고 끄기, 밀기·‹ ›로 이동, 막대 끌 때는 안 넘어감, 스크립트 끄면 기본 막대·‹ › 링크로 동작, 기존 반응·한마디 e2e 통과
- 범위 밖(다음): 사진 크게 보기 PC 배치 세부, 넘겨 보기·크게 보기 외 화면

### 30. feature/parent-nav — 부모 화면 이동 표시 정리 (디자인 버전 107, 디자인 시스템 README 18)

- 요구사항(사용자 2026-10-26, 디자인 먼저 고친 뒤 적용)
  - 아래 탭에 알림 추가: 앨범 · 알림 · 설정. 알림 탭에 새 반응 수 배지. 최근 반응 화면은 알림 탭 첫 화면(큰 제목 "알림", 뒤로가기 없음). 앨범 위 "최근 반응" 줄 삭제
  - 앨범 위 접종 줄 → 아이 카드: 콩이 + 이름 · 생후 N개월 · 태어난 지 N일 + 다음 일정. 카드 전체가 접종·검진 링크, "다음"·"일정" 글자 없이 오른쪽 꺾쇠만. 위아래 가운데 정렬
  - 누르면 넘어가는 줄·띠는 오른쪽 꺾쇠 아이콘만: 승인 요청·홈 화면 부탁 띠의 "확인 ›"·"문자 ›", 그룹 비밀번호 "바꾸기", 아이 "고치기" → 꺾쇠. 글자 ›는 같은 모양 선 아이콘으로
  - 왼쪽 위 뒤로가기는 글자만("설정", "앨범"…, ‹ 없음). 가족 크게 보기 "닫기"도 글자만(어르신이 헷갈리지 않게 한 규칙으로)
- 구현 방식: `Parent.astro`에 알림 탭과 `alerts` 배지(각 화면이 `a.home.new_activity` 전달, 알림 화면은 0). `.sp-p__chev`는 CSS mask로 선 아이콘, 띠·카드는 인라인 svg(`.sp-p__icon-chev`). 아이 카드 `.sp-p__kid`. 콩이는 지금 있는 `/favicon.svg`(나이별 7단계 그림은 아직 없음)
- 영향받는 파일: `src/layouts/Parent.astro`, `src/pages/home.astro`, `src/pages/reactions.astro`, 탭 있는 부모 화면 17개(배지 전달·뒤로가기 글자), `src/pages/settings/children/index.astro`, `src/pages/settings/family/groups/[id]/index.astro`, `src/pages/album/[id].astro`(닫기), `src/styles/parent.css`, `plan.md`
- 예상 결과: 알림 탭·배지·아이 카드·꺾쇠·글자 뒤로가기(스크린샷), reactions·health·install 등 e2e 통과
- 결과: e2e(reactions·install·health·settings2·groups·members·parent·family·vplay) 통과. 범위 밖: 설정 탭의 승인 배지(디자인엔 있음, 코드엔 원래 없음), 나이별 콩이 그림

### 31. feature/center-layers — 가운데 레이어 3종 (디자인 버전 109)

- 요구사항(사용자 2026-10-26, 조사·추천 1–3번 확정): 앱을 열 때 꼭 알아야 할 일만 가운데 레이어로. 같은 일은 한 번만, 한 번 열 때 하나만, 저절로 사라지지 않음
  1. 부모 앨범: 들어오기 신청(새 휴대폰 포함). "큰이모가 외가 앨범에 들어오려고 해요" + 신청 시각·3일 뒤 자동 취소 [확인하기 → 가족 설정] [나중에]
  2. 가족 앨범: 승인 뒤 처음 열 때 콩이 + "엄마아빠가 확인했어요 / 이제 ○○ 사진을 모두 볼 수 있어요" [사진 보기]
  3. 가족 앨범: 지난번 이후 새로 올라온 사진이 있을 때 "○○ 새 사진 N장이 왔어요" + 썸네일 3칸(+N) + "○월 ○일에 올라왔어요" [보기]. 가족은 2가 3보다 먼저
- 구현 방식(DB 칸 추가 없음, 기기별 쿠키)
  - "봤음"은 기기 쿠키에 기록: `sp_join_seen`(부모, 마지막으로 닫은 신청 시각), `sp_waited`(가족, /wait에서 기다리던 가족방 id), `sp_photos_seen`(가족, 마지막으로 본 사진의 올린 시각). 1년, httpOnly·lax
  - 버튼은 폼 POST(PRG)로 쿠키를 적고 돌아감 → 가족 화면 JS 0KB 유지. 레이어는 서버가 `<dialog open>`로 그리고 첫 버튼에 autofocus
  - 새 사진 판단에 사진의 올린 시각이 필요해 `MediaItem`에 `created_at` 추가(DB 열은 이미 있고 읽기 권한도 있음, 목록 select만 추가)
  - 처음 오는 기기는 쿠키가 없으므로 3번을 띄우지 않고 지금 사진까지 본 걸로 기록(카톡으로 막 들어온 사람에게 "새 사진" 레이어는 군더더기)
- 영향받는 파일: `src/lib/backend/types.ts`, `src/lib/backend/supabase.ts`, `src/lib/backend/mock.ts`, `src/lib/layers.ts`(쿠키 이름·읽기), `src/pages/home.astro`, `src/pages/album/index.astro`, `src/pages/wait.astro`, `src/styles/base.css`(레이어 공통), `plan.md`
- 예상 결과: 각 레이어가 조건에서 한 번만 뜨고 버튼 뒤 다시 안 뜸(e2e), 다크·라이트 스크린샷
- 확인 필요: 기기 쿠키라 브라우저를 바꾸거나 쿠키를 지우면 2·3이 다시 뜰 수 있음(3은 지금 사진 기준이라 영향 적음). 레이어가 열린 동안 뒤 화면도 Tab으로 갈 수 있음(JS 없이 inert를 걸 수 없음). '새 사진'은 올리기 시작 시각(created_at) 기준이라 여러 장을 동시에 올릴 때 먼저 끝난 늦은 사진이 기준을 올리면 앞 사진이 안내에서 빠질 수 있음(정확히 하려면 준비된 시각 열 필요). 한 집만 거른 화면(?f)에선 레이어·기록 안 함. 최근 200장 밖(찍은 날이 아주 오래된 사진)은 안내 안 됨. 기존 기기가 다시 승인 대기로 바뀌면 만든 시각이 옛날이라 신청 레이어가 안 뜰 수 있음(띠는 뜸)
- 결과: 검토 반영(빈 앨범 첫 방문은 지금 시각으로 기록, ?f 화면 제외, 새 휴대폰 신청엔 3일 문구 빼기, 설명 연결·autofocus 하나). layers e2e 13개, 기존 e2e는 레이어 자동 닫기 도우미로 통과

### 32. feature/layers-milestone-storage — 가운데 레이어 4·5 (완료, dev 머지, 디자인 버전 111)

- 요구사항(사용자 2026-10-26 "2번 둘 다 지금 진행"): 부모 앨범에
  4. 백일·돌·생일 당일: 콩이 + "오늘은 하린이 태어난 지 100일이에요"(돌: "첫 생일이에요", 그 뒤 "두 번째 생일이에요") + "오늘 찍은 사진을 올려서 가족과 함께 축하해요" [사진 올리기 → /upload] [닫기]
  5. 저장 공간 90% 이상(무료 5GB): "저장 공간이 거의 찼어요"(100%면 "다 찼어요") + 막대 + "5GB 중 4.6GB를 쓰고 있어요…" [저장 용량 보기] [나중에]
  5-2. 가족 플랜 7일 안에 끝남: 디자인만(LayerPlan). 코드는 결제 이슈에서(지금은 플랜·결제가 없어 갈 화면이 없음)
- 구현 방식: 31과 같은 기기 쿠키 + 폼 POST(PRG). 한 번 열 때 하나만, 순서는 들어오기 신청 → 백일·생일 → 저장 공간
  - `sp_milestone_seen`: 본 날 키(`아이id:YYYY-MM-DD`). 그날만 뜸, 닫으면 그날 다시 안 뜸
  - `sp_storage_seen`: 본 단계(`90`/`100`). 90에서 닫아도 100이 되면 한 번 더. 90 밑으로 내려가면 쿠키를 지워 다음에 다시 넘으면 또 뜸
  - 날짜 계산은 `src/lib/age.ts`에 `milestone(birth, today)` 추가(서울 날짜, 태어난 날이 1일째) + 단위 테스트
- 영향받는 파일: `src/lib/age.ts`, `tests/age.test.ts`, `src/lib/layers.ts`, `src/pages/home.astro`, `plan.md`
- 예상 결과: 조건 날에만 한 번 뜨고 버튼 뒤 다시 안 뜸(e2e), 스크린샷
- 결과: layers45 e2e 9개(백일·저장 공간·돌·평범한 날), 기존 layers·health·members 통과, 단위 22개. 저장 공간 확인용으로 mock에 `SWEEPEA_MOCK_USED_BYTES` 추가. 막대는 35에서 키컬러로 통일
- 확인 필요: 2월 29일생은 평년엔 생일 레이어 없음. 가족 플랜 레이어는 자동 갱신을 끈 사람에게만 띄울지(스토어 구독 상태 필요), 끝난 뒤 정책 문구

### 33. feature/settings-badge — 설정 탭 승인 대기 배지 (완료, dev 머지, 디자인 버전 112)

- 요구사항(사용자 2026-10-26 "추가되어야 확인하지"): 부모 아래 탭 '설정'에 승인 기다리는 사람·휴대폰 수 배지(`blossom`), 화면 읽기는 "설정, 승인 기다리는 사람 N명"
- 구현 방식: 부모 첫 화면 정보(`sp_parent_home`)에 `waiting`(기한 안 지난 들어오기 신청 + 승인 기다리는 휴대폰) 추가 → 탭 있는 모든 화면이 레이아웃에 넘김. 마이그레이션은 아직 적용 전이라 parent_home 파일을 직접 고침
- 영향받는 파일: `supabase/migrations/20261025000006_parent_home.sql`, `src/lib/backend/types.ts`, `src/lib/backend/mock.ts`, `src/layouts/Parent.astro`, 탭 있는 부모 화면 17개, `plan.md`
- 예상 결과: 신청이 오면 설정 탭에 숫자, 승인하면 사라짐(e2e), 스크린샷
- 같이 정리: 켜고 끄기는 토글로 결정(디자인을 토글로 고침, 코드는 이미 토글, 디자인 시스템 README 19)
- 결과: badge e2e 5개, 기존 members·layers·parent 통과. 확인 필요: parent_home SQL은 실제 DB에서 아직 안 돌려 봄(DB 설정 뒤)

### 34. feature/kid-tabs — 폰·PC 통일: 아이 고르기 세그먼트 탭 (완료, dev 머지, 디자인 버전 113)

- 요구사항(사용자 2026-10-26 "1, 2 진행 완료"): 폰·PC는 같은 컴포넌트, 배치만 다르게. 아이 고르기는 라디오 칩 대신 한 줄 좌우 스크롤 세그먼트 탭
- 디자인(버전 113): PC 보드를 코드의 넓은 화면 배치에 맞춤 — 부모 PC 앨범(위 메뉴 = 폰 탭 3개, 아이 카드 = 폰 카드, 세그먼트 탭, 떠 있는 '사진 추가하기'), 부모 PC 올리기(폰과 같은 '취소 / 사진 N장' 줄), 가족 PC 모아 보기(폰과 같은 제목·세그먼트·떠 있는 −/+), PC 크게 보기(넘기기 안내 문구 삭제). 폰 올리기 '아이'도 그룹과 같은 체크 칩
- 코드: 부모 앨범에 아이가 둘 이상이면 `전체 · 하린 · 도윤` 탭(`?k=아이id` 링크, aria-current). 고른 아이 사진만(사진-아이 연결), 아이 카드도 그 아이만
  - `listMedia`에 `childId` 추가: supabase는 `media_children!inner` 필터, mock은 childIds
- 영향받는 파일: `src/lib/backend/types.ts`, `supabase.ts`, `mock.ts`, `src/pages/home.astro`, `src/styles/parent.css`, `plan.md`
- 예상 결과: 탭 누르면 그 아이 사진만, 폰은 가로 꽉, PC는 글자 폭만큼, 넘치면 옆으로 밀림(e2e)
- 결과: kidtabs e2e 11개, 기존 parent·health·upload 통과. 탭은 아이 카드 아래(디자인 순서). 확인 필요: supabase `media_children!inner` 필터는 실제 DB에서 아직 안 돌려 봄. 부모 앨범 칸 모양(코드 정사각 / 디자인 높이 제각각)은 그대로 둠

### 35. feature/design-gaps — 디자인·코드 차이 정리 (완료, dev 머지, 디자인 버전 114)

- 요구사항(사용자 2026-10-26 "2 진행 완료"): 비교에서 찾은 차이 정리. 있는 데이터로 할 수 있는 건 코드를 디자인에, 데이터가 없는 건 디자인을 코드에
- 코드: 목록 줄 사이 구분선(`.sp-p__list > * + *`, li라 전체 선택자), 저장 막대(meter)를 키컬러 하나로(브라우저 기본 노랑 대신, 고대비 모드는 기본), 구성원 상세 부제에 마지막으로 본 날("가족 · 휴대폰 1대 · 오늘")
- 디자인: 구성원 상세 부제를 코드 표기로, '올린 사진'·'가족 화면 글자 크기' 줄 삭제(구성원별 올린 수·글자 크기 데이터 없음, 원격 글자 크기는 범위 밖), 안내 문구를 코드 문구로. 저장 막대는 분홍 → 키컬러(blossom은 하트에만)
- 결과: 기존 settings2·members·groups e2e 통과, 스크린샷 확인
- 남김: 가족 플랜 줄·카드(결제 이슈에서), 설정 하위 화면 제목 배치(디자인은 가운데 작은 제목, 코드는 큰 제목)

### 36. feature/db-setup — 실제 Supabase 연결 (완료, dev 머지)

- 요구사항(사용자 2026-10-26 "3번 진행하자"): mock이 아닌 실제 Supabase에 스키마를 올리고 화면을 실제 백엔드로 확인
- 지우님이 할 일(둘 중 하나)
  - A(선택됨): Supabase 커넥터 연결(커넥터는 조직 하나만 고를 수 있어 sweepea 조직으로)
  - B: supabase.com에서 프로젝트를 직접 만들고 Project URL, anon 키, service_role 키, DB 비밀번호를 알려 주기(service_role·DB 비밀번호는 이 대화 대신 `.dev.vars`에 직접 넣어도 됨)
- 구현 방식(연결 뒤)
  1. 마이그레이션 13개를 순서대로 적용(로컬 Postgres 16 검사는 통과: `npm run test:db`, 의도된 거부 48건). 적용 뒤부터 init 직접 수정 금지, 새 파일로
  2. Auth: 익명 로그인 켜기(가족 기기), 부모 로그인 제공자(카카오 먼저, 나머지는 키 받은 뒤), 사이트 주소·리다이렉트 주소
  3. `.dev.vars`(git 제외)에 SUPABASE_URL·SUPABASE_ANON_KEY·SUPABASE_SERVICE_ROLE_KEY·MEDIA_URL_SECRET, `SWEEPEA_BACKEND=supabase`로 개발 서버
  4. 실제 백엔드로 핵심 흐름 확인: 부모 처음 설정 → 링크 → 가족 입장·승인 → 올리기(R2는 로컬 miniflare) → 보기·반응 → 아이 탭(`media_children!inner`)·배지(waiting)·사진 정보
  5. 운영 배포(Cloudflare 시크릿·R2 버킷)는 다음 이슈
- 영향받는 파일: 확인 중 나오는 버그 수정만(supabase.ts 등), `.dev.vars.example`, `index.md`, `plan.md`
- 진행(2026-10-26): 프로젝트 `sweepea`(ref aemzbelwyyweugxuqgoh, 서울, 무료 조직) 생성. 마이그레이션 13개 적용 완료(커넥터, 같은 이름). 보안 점검: 정책 없는 표 2개(entry_failures·r2_cleanup, 의도: 함수만 씀), 로그인 사용자가 부르는 security definer 함수 31개·anon `sp_entry_info`(의도: 권한 판정을 함수 안에서 함). `.dev.vars.supabase`(git 제외)에 URL·anon 키
- 대시보드(지우님): 익명 로그인 켬, 이메일 확인 잠시 끔(테스트 부모 계정용), secret 키 `dev-test` 발급 → `.dev.vars.supabase`
- 결과: 실제 Supabase로 핵심 흐름 e2e 11개 통과 — 처음 설정, 아이 추가, 사진 올리기(완료 처리 = secret 키로 sp_finish_upload), 아이 탭(`media_children!inner` 필터), 링크 → 새 이름 입장 → 설정 탭 배지(waiting) → 승인 → 승인 완료 레이어 → 가족 앨범 → 반응 → 부모 알림 배지. 부모는 이메일 테스트 계정 토큰을 sp_parent 쿠키에 직접 넣어 확인(앱 화면엔 이메일 로그인 없음). 코드 수정 없이 통과
- 실제 DB로 아직 안 돌린 것: 사진 정보 고치기·지우기, 그룹, 탈퇴·되살리기, 정리 예약 작업, 승인 대기 휴대폰(10번 틀림). R2는 로컬(miniflare)
- 확인 필요: 카카오 로그인은 카카오 개발자 앱(REST 키·Client Secret)이 있어야 켤 수 있음. 무료 조직은 1주 쉬면 프로젝트가 멈춤
- 확인 필요(출시 전): 익명 가입 남용 막기(CAPTCHA·가입 횟수 제한), 테스트 데이터(가족방·테스트 계정) 지우기

### 37. feature/deploy — Cloudflare Workers 첫 배포 (완료, dev 머지)

- 요구사항(사용자 2026-10-26 "배포 먼저 가볼까?"): 실제 Supabase + 진짜 R2로 인터넷에서 열리는 주소
- 구현 방식
  1. 먼저 `*.workers.dev` 주소로 배포(도메인 연결은 그다음)
  2. R2 버킷 `sweepea-media` 만들기(wrangler.jsonc 그대로)
  3. 시크릿: SUPABASE_URL·SUPABASE_ANON_KEY(공개)·MEDIA_URL_SECRET(새로 만듦)·SITE_ORIGIN, SUPABASE_SERVICE_ROLE_KEY는 **운영용 secret 키를 지우님이 Cloudflare 대시보드에 직접**(대화에 남기지 않게). PARENT_PROVIDERS는 카카오 연결 전까지 비움(로그인 화면은 "준비되지 않았어요")
  4. 매일 정리 예약(18:17 UTC)은 wrangler.jsonc 그대로 올라감
  5. 배포 뒤 확인: 첫 화면·로그인 화면·가족 링크 화면 응답, 사진 전달 경로, 보안 헤더
  6. Supabase Auth 사이트 주소·리다이렉트에 배포 주소 추가(카카오 연결 때 필요)
- 배포 방법: 지우님이 Cloudflare API 토큰(Workers 스크립트·R2 편집 권한)을 만들어 주면 여기서 `wrangler deploy`. 토큰은 배포 끝나면 지우님이 삭제
- 진행(2026-10-26): 계정 `Takeaseat.cs@gmail.com's Account`(workers.dev 이름 takeaseat-cs, 기존 Worker tas-proxy 있음). R2 켬(지우님, 무료 구간), 버킷 `sweepea-media`(apac) 만듦, 배포 → **https://sweepea.takeaseat-cs.workers.dev** (매일 18:17 UTC 예약 포함). 시크릿 SUPABASE_URL·SUPABASE_ANON_KEY·MEDIA_URL_SECRET(새로 만듦, 여기 안 남김) 넣음. SITE_ORIGIN은 비움(요청 주소로 링크 만듦, 도메인 연결 때 넣기)
- 배포 확인: 첫 화면 200, 로그인 200("준비되지 않았어요"), /home → /start, 없는 가족 링크 → 안내 화면, 정적 파일 200
- 지우님: 운영용 secret 키 `prod`를 Cloudflare에 직접 넣음(SUPABASE_SERVICE_ROLE_KEY, 시크릿 4개 확인), Supabase 사이트 주소·리다이렉트
- 결과: 배포 주소에서 실제 Supabase + 진짜 R2로 핵심 흐름 e2e 11개 통과(처음 설정·올리기·아이 탭·입장·배지·승인·레이어·반응·알림). R2에 view·thumb 파일 저장 확인. 콩이 움직임(38)도 같이 배포
- 정리(2026-10-26 확인): 이메일 확인 다시 켬, Cloudflare 토큰 무효 확인, Supabase dev-test 키 삭제. 이후 배포는 44(자동 배포)
- 확인 필요: 화면 응답에 보안 헤더(X-Frame-Options/CSP frame-ancestors·Referrer-Policy 등)가 사진 전달(/m)에만 있음. 가족 링크 주소(/i/코드)가 Referer로 새지 않게 다음 이슈에서 공통 헤더 추가
- 영향받는 파일: `wrangler.jsonc`(필요하면), `index.md`, `plan.md`
- 확인 필요: Cloudflare 계정·요금제(무료면 요청당 외부 호출 50개 → 정리 작업이 나눠서 돎), sweepea.co.kr 등록·DNS 위치
### 38. feature/kongi-hop — 콩이 통통 움직임 (완료, dev 머지)

- 요구사항(사용자 2026-10-26 "콩 들어있는데는 전반적으로 움직이게"): 디자인 시스템 규칙(2.4초마다 통통 두 번, steps로 끊어서, 여러 마리면 0.3초씩 늦게, 동작 줄이기면 멈춤)을 코드에. 디자인 캔버스는 이미 움직임(`sp-kongi-anim`)이라 디자인 수정 없음
- 구현: `base.css`에 `sp-kongi-hop` 하나, 콩이 클래스 7개(부모 소개·빈 앨범·아이 카드·소개 시안, 가족 입장·앨범, 가운데 레이어)에 적용. 아이 카드가 여러 개면 두 번째부터 0.3초씩 늦게
- 영향받는 파일: `src/styles/base.css`, `plan.md`

### 39. feature/security-headers — 공통 보안 헤더 (완료, dev 머지)

- 요구사항(37에서 발견, 사용자 2026-10-26 "응"): 사진 전달(/m) 말고는 보안 헤더가 없음. 다른 사이트가 틀(iframe)에 넣어 누르게 하는 공격, 가족 링크(/i/코드)·사진 주소가 Referer로 밖에 새는 것 막기
- 구현: `src/middleware.ts`(모든 화면 응답) — X-Content-Type-Options nosniff, Referrer-Policy no-referrer, X-Frame-Options DENY, CSP `frame-ancestors 'none'; base-uri 'self'; object-src 'none'; form-action 'self'`, Permissions-Policy(카메라·마이크·위치 끔), 운영에서만 HSTS. 이미 있는 헤더(/m의 sandbox CSP)는 덮지 않음. 정적 파일은 `public/_headers`로 nosniff·no-referrer
- 전체 CSP(script-src 등)는 화면마다 인라인 스크립트가 있어 이번엔 안 함(확인 필요로)
- 영향받는 파일: `src/middleware.ts`(새), `public/_headers`(새), `plan.md`
- 예상 결과: 화면·리다이렉트·정적 파일 응답에 헤더(e2e), 기존 e2e 통과, 배포 뒤 확인
- 결과: 개발 서버에서 화면·리다이렉트·404·가족 링크 응답 헤더 확인, 기존 parent·members·layers·vplay e2e 통과. 확인 필요: 전체 CSP(script-src·img-src)는 인라인 스크립트를 해시로 바꾼 뒤

### 40. feature/kongi-asset — 콩이만 움직이게 (완료, dev 머지)

- 요구사항(사용자 2026-10-26 "콩만 움직여야지 배경은 움직이지 말고"): 코드는 콩이 자리에 앱 아이콘(`favicon.svg`, 둥근 바탕 칸 포함)을 써서 바탕까지 같이 뛰었음. 디자인 캔버스 콩이는 바탕 없는 그림이라 코드만 달랐음
- 구현: 디자인의 콩이 그림(3단계 떡잎, 바탕 없음)을 `public/kongi.svg`로 넣고 콩이 자리 8곳을 바꿈. 앱 아이콘(`favicon.svg`)은 탭 아이콘으로만
- 영향받는 파일: `public/kongi.svg`(새), `src/components/Notice.astro`, `src/pages/home.astro`, `src/pages/start.astro`, `src/pages/album/index.astro`, `src/pages/login/index.astro`, `plan.md`
- 확인 필요: 콩이 나이별 7단계 그림은 아직 3단계 하나로 씀

### 41. feature/kakao-login — 부모 카카오 로그인 연결 (완료)

- 요구사항(사용자 2026-10-26 "그럼 카카오"): 배포된 사이트에서 부모가 카카오로 로그인
- 지우님이 할 일: 카카오 개발자 앱 만들기(스위피) → REST API 키·Client Secret → 카카오 로그인 켜기, Redirect URI `https://aemzbelwyyweugxuqgoh.supabase.co/auth/v1/callback`, 동의항목 닉네임(필수 아님 최소) → Supabase Kakao 켜기 + 키 두 개 + "Allow users without an email" → Cloudflare 변수 `PARENT_PROVIDERS=kakao`
- 구현 방식: 코드는 이미 있음(PKCE, `/login/kakao` → Supabase → `/auth/callback`). 이메일은 받지 않음(비즈 앱 필요, 쓸 데 없음). 카카오가 이메일 범위 때문에 거절하면 authorize 주소에 범위를 직접 지정
- 영향받는 파일: 필요하면 `src/lib/backend/supabase.ts`(parentAuthorizeUrl), `plan.md`
- 예상 결과: 지우님 휴대폰으로 배포 주소에서 카카오 로그인 → 처음 설정 → 앨범
- 결과(2026-10-26): 지우님 휴대폰으로 배포 주소에서 카카오 로그인 성공(가족 설정 화면까지). 겪은 것: KOE101(REST API Key 칸에 'sweepea'), KOE205(Supabase는 이메일·프로필 사진·닉네임을 늘 요청 → 카카오 동의항목을 맞춤), localhost로 감(Supabase URL Configuration 미저장). 코드 수정 없음
- 같이 고침(44 자동 배포로 올라감): fix/group-link — 가족 화면 '그룹 관리' 칩이 실기기에서 깨짐 → 디자인대로 '가족 그룹 ›' 제목 링크. fix/alerts-empty — 알림 화면에 반응이 없으면 안내 두 줄이 겹쳐 보임 → 빈 안내 하나만(reactions e2e의 배지 검사를 알림 탭으로 좁힘: 설정 배지가 생겨서 오판)
- 확인 필요: 카카오에서 받는 이메일·사진은 쓰지 않으니 개인정보 처리방침에 적고, 나중에 직접 OIDC로 닉네임만 받는 방식 검토
- 확인 필요: 도메인(sweepea.co.kr)은 실제 가족에게 링크 보내기 전에 등록·연결(링크가 주소에 묶이고, 주소가 바뀌면 가족 기기가 다시 들어와야 함). .co.kr은 국내 등록 업체에서 사고 네임서버만 Cloudflare로

### 42. feature/save-many — 가족 모아 보기에서 여러 장 골라 저장 (완료, dev 머지, 디자인 버전 115)

- 요구사항(사용자 2026-10-26 "선택해서 여러개 저장" → 가족 모아 보기, 한 장씩 연달아 저장): 엄마아빠가 '가족도 사진 저장하기'를 켠 가족방 사진만
- 구현 방식
  - 모아 보기에 [골라서 저장하기] 링크(저장 허용된 집이 하나라도 있을 때) → `/album/save`(같은 쿼리)
  - `/album/save`: 체크박스 폼(GET, name=id). 사진을 누르면 초록 테두리·체크(`:has(:checked)`), 아래 고정 버튼. 저장 허용 안 된 집 사진은 목록에서 뺌
  - 스크립트(이 화면만, 가족 화면 JS 예외 2번째): 고른 수 표시, 버튼 문구 'N장 휴대폰에 저장하기', 누르면 파일을 받아 **휴대폰은 공유 창(이미지 저장)**, 공유 창이 없으면(PC) 한 장씩 내려받기
  - 스크립트 없을 때: 버튼을 누르면 고른 사진마다 [저장] 링크가 있는 목록(한 장씩 누름)
- 영향받는 파일: `src/pages/album/save.astro`(새), `src/pages/album/index.astro`, `src/styles/family.css`, `index.md`, `plan.md`
- 예상 결과: 고르기·수 표시·저장 시도(e2e, PC 내려받기 이벤트), 스크립트 없이 목록, 저장 안 되는 집 사진 제외, 큰 글씨 화면 스크린샷
- 결과: save e2e 10개(저장 꺼짐이면 버튼 없음·화면 막음, 고르기·빼기·장수, PC 2장 내려받기, 스크립트 없이 저장 링크). 고르면 바로 파일을 미리 받아 둠(누른 직후 공유 창을 열어야 휴대폰이 막지 않음). 확인 필요(실기기): 아이폰·안드로이드 공유 창에서 '이미지 저장'으로 사진 앱에 들어가는지, 영상 여러 개(용량 큼)일 때 메모리

### 43. fix/toast-float — 완료 안내 토스트 (완료, dev 머지)

- 요구사항(사용자 2026-10-26 "사진 지우고나면 메세지 사라져야지, 토스트로"): '지웠어요.' 같은 완료 안내가 칸으로 계속 남아 있었음
- 구현: CSS만. 부모 화면 완료 안내(`.sp-p__toast`, 실패 `--error`·올리기 진행 `--live` 제외)를 화면 위 가운데 반투명 알약으로 띄우고 4초 뒤 사라짐(동작 줄이기면 미끄러짐 없이 사라지기만, 투명도 줄이기면 채운 바탕). 아래엔 '사진 추가하기'가 있어 위에
- 결과: 4초 뒤 숨김 확인, settings2·members·groups·health e2e 통과
- 확인 필요: 주소의 `?done=…`이 남아 새로고침하면 다시 뜸(스크립트 없이 지우려면 PRG 한 번 더)


### 44. chore/auto-deploy — dev 푸시하면 자동 배포 (완료)

- 요구사항(사용자 2026-10-26 "설정해두고 계속 되게 못해"): 배포 때마다 토큰을 새로 만들지 않기
- 방식: Cloudflare Workers Builds를 GitHub `mjkang0987/sweepea`에 연결(지우님). 운영 브랜치 `dev`, 빌드 `npm run build`, 배포 `npx wrangler deploy`, 경로 `/`, 미리보기 빌드 끔(feature 브랜치가 실제 DB·R2를 건드리지 않게). 빌드 토큰은 Cloudflare가 만들어 보관
- 연결만으로는 빌드가 돌지 않아 이 기록 커밋을 dev에 푸시해 첫 빌드를 띄움
- 출시 때: 운영 브랜치를 `main`으로 바꾸기

### 45. feature/settings-version — 설정 맨 아래 버전 (완료, dev 머지, 디자인 버전 117)

- 요구사항(사용자 2026-10-26 "뭐 하나 배포해줘 테스트보게"): 자동 배포 확인용. 휴대폰에서 지금 몇 버전인지 보이게
- 방식: 설정 화면 맨 아래 "스위피 0.2.1"(package.json 버전). 버전 0.2.0 → 0.2.1
- 결과: 타입 검사·단위 테스트·e2e(ver.py) 통과, dev 푸시로 자동 배포

### 46. fix/photo-nav — 사진 정보 넘겨보기·날짜 칸 넘침 (완료, dev 머지, 디자인 버전 118)

- 요구사항(사용자 2026-10-26 실기기 캡처 "틀어지고 넘겨보기 안돼"): 사진 정보 화면에서 날짜 칸이 오른쪽으로 넘침, 옆 사진으로 못 넘어감
- 원인: 아이폰 사파리 날짜 입력칸은 기본 모양일 때 width를 무시하고 내용 폭으로 넓어짐 → 공통 `.sp-p__input[type=date]`에 appearance:none(올리기·아이 추가 화면도 같이 고침)
- 넘겨보기: 사진 위 ‹ › 링크(스크립트 없이도 됨) + 옆으로 밀기 작은 스크립트. 순서는 앨범과 같음(최근 200장, 아이를 골랐으면 `?k=` 이어받아 그 아이 사진만)
- 결과: 타입 검사·단위 테스트·e2e(nav.py 8개, photo.py) 통과. 날짜 칸 넘침은 크롬에서만 확인, 아이폰 실기기 확인 필요

### 47. feature/photo-swiper — 사진 정보 진짜 스와이퍼 (완료, dev 머지)

- 요구사항(사용자 2026-10-26 "매번 페이지로드하면 불편해서", 진짜 스와이퍼 선택): 넘길 때 페이지를 다시 부르지 않고 손가락을 따라 넘김
- 방식: 서버가 앞뒤 20장 주소를 서명해 넘기고, 스크립트가 CSS 스크롤 스냅 트랙으로 바꿈. 멈추면 주소만 바꾸고(replaceState) 그 사진 화면을 받아 아래 한마디·날짜·아이·그룹 칸만 갈아 끼움. 폼은 action에 사진 id를 박아 늘 그 칸의 사진에 저장. 스크립트가 없으면 한 장 + ‹ › 링크
- 같이 고침: 사진 칸이 `figure` 기본 여백 때문에 좁고 가운데로 몰려 있었음 → div로
- 디자인: 생김새는 버전 118 그대로(화살표). 사진 칸 높이는 디자인 260px, 코드는 화면 60%
- 결과: 타입 검사·단위 테스트·e2e(swiper.py 11개, photo.py) 통과. nav.py는 swiper.py로 대체
- 다음: 가족 크게 보기(`/album/[id]`)도 스와이퍼로(반응·한마디·저장 링크까지 갈아 끼워야 함)
- 고침(사용자 "버튼 늦게 없어져", "촬영날짜 중앙정렬 안됐어"): 화살표를 멈춘 뒤가 아니라 미는 동안 바로 바꿈, 멈춤 알림(scrollend)이 있으면 바로 정보 칸 교체. 날짜 칸은 기본 모양을 끄면 아이폰이 글자를 위에 붙여서 줄 높이로 세로 가운데(가로는 다른 입력칸처럼 왼쪽 — 사용자 의도 확인 필요). 0.2.4
- 고침(사용자 "사진 위아래 여백"): 칸 높이를 화면 60%로 고정해서 가로 사진은 위아래가 회색 빈 칸으로 남았음 → 지금 사진 비율에 맞춰 칸 높이를 바꿈(화면 60%까지, 0.2초 전환). 아주 긴 세로 사진은 60%에서 멈춰 좌우가 빔. 0.2.5

### 48. feature/parent-gallery — 엄빠도 조부모와 같은 갤러리 (계획)

- 요구사항(사용자 2026-10-27 "엄빠도 갤러리 보긴 해야할거같아"): 엄빠가 앨범에서 사진을 누르면 조부모처럼 화면 가득 넘겨 보기. 지금은 바로 '사진 정보'(관리 화면)로 감
- 진행 방식(사용자 2026-10-27): 원인·계획 먼저 보고 → 개발 → 코드 리뷰·검증·기능 리뷰 3회차 → 머지
- 현재 구조
  - 가족 크게 보기 `/album/[id]`: Family 레이아웃, 가족 출입증 쿠키(loadAlbum), 반응·한마디·저장 링크, 넘길 때마다 페이지를 새로 부름
  - 엄빠 사진 정보 `/photo/[id]`: 관리 화면 + 스와이퍼(47)
- 구현 방식(안)
  1. 디자인 먼저: 엄빠 크게 보기 보드(다크·라이트). 조부모 크게 보기와 같은 화면(반응·한마디 남기기·저장) + 엄빠만 '사진 정보 수정' 플로팅 버튼(사용자 2026-10-27). 엄빠 업로드 화면은 그대로
   - 엄빠도 반응·한마디를 남김(사용자 2026-10-27 "처음부터 남기기까지")
  2. 크게 보기 화면을 공통 부품으로 빼서 엄빠·가족이 같이 씀. 스와이퍼(손가락 따라 넘김, 페이지 안 부름)도 이 부품에서 한 번만
  3. 엄빠 경로 `/view/[id]`(탭 없이 화면 가득, 아이 고르기 `?k=` 이어받기). 앨범 격자 → `/view`, 크게 보기 '정보 수정' 버튼 → `/photo/[id]`(수정 화면)
  4. 사진 정보 → '정보 수정' 화면(사용자 2026-10-27 "하단에서 고치는 거 말고 버튼으로 수정 진입"): 크게 보기에는 입력칸을 두지 않고 버튼으로만 들어감. 수정 화면은 작은 미리보기 + 날짜·아이·그룹·지우기, 저장하면 크게 보기의 그 사진으로 돌아감. 스와이퍼는 크게 보기로 옮김
  5. 가족 `/album/[id]`도 공통 부품으로 갈아타 스와이퍼 적용(반응·한마디·저장 링크를 사진마다 갈아 끼움)
- 영향 파일: src/components/(새 크게 보기 부품), src/pages/view/[id].astro(새), src/pages/album/[id].astro, src/pages/photo/[id].astro, src/pages/home.astro, src/styles/family.css·parent.css, e2e
- 예상 결과: 엄빠·가족 모두 사진을 화면 가득 손가락으로 넘겨 봄. 스크립트가 없으면 ‹ › 링크로 넘김
- 조사(2026-10-27): 반응·한마디 표는 `member_id`(링크로 들어온 가족)만 받는다. 부모 계정은 `parents` 한 명(배우자는 구성원으로 들어옴)이라 반응을 남길 자리가 없음
  - 고칠 곳: reactions·comments에 `parent_user_id` 열 추가(둘 중 하나만), reactions 기본 키 → 고유 색인 2개, 부모용 RPC(sp_parent_react·sp_parent_comment), 반응 수(sp_reaction_counts)·한마디 목록·부모 새 반응 수(내 반응은 빼기)·최근 반응 목록에 부모 포함, RLS·DB 검사(rls.sql)
  - 조부모 화면에는 부모 이름으로 보임(parents.display_name, 예: '하린 엄마')
- (가) 디자인 완료: 버전 119(ParentView·ParentView-Light 새 보드, ParentPhoto → 사진 정보 수정: 닫기·저장 버튼·작은 미리보기)
- (나) DB 완료(feature/parent-react-db, dev 머지): 마이그레이션 20261027000001_parent_reactions, 백엔드 parentReact·parentComment. 리뷰 3회차
  - 1회차(별도 리뷰): 가족이 reactions.parent_user_id(부모 사용자 id)를 읽을 수 있었음 → 열 권한으로 막음. 탈퇴 유예 중 부모 반응 막음. 부모 지울 때 찾는 색인. 검사 추가(다른 집 부모, 하루 30개, 지우기, 탈퇴 유예)
  - 2회차: mock과 DB 동작 대조(부모 이름 '엄마/아빠' = 실제 parents.display_name), parents 읽기 정책 확인
  - 3회차: DB 검사(의도된 거부 58건), 타입 검사, 단위 테스트, e2e(reactions·photo·swiper) 통과
  - 남은 것: 부모는 자기 한마디를 고칠 수 없음(지우기만, 가족도 고치는 화면은 아직 없음)
- (다) 공통 갤러리 + 엄빠 갤러리 완료(feature/parent-view): src/components/Viewer.astro(가족·엄빠 공통), /view/[id](엄빠, 부모 계정으로 반응·한마디, 늘 저장, '사진 정보 수정' 플로팅 버튼), 앨범 격자 → /view. 폼 처리 applyReactPost 공통화. 리뷰 3회차
  - 1회차(별도 리뷰): 큰 글씨·가로 화면에서 수정 버튼이 저장 링크를, › 화살표가 수정 버튼을 가림 → 판+버튼 묶음(.sp-v__dock)을 화면 75%로 제한, 버튼을 화살표 위로, 판이 가운데까지 오면 화살표를 판 위로(스크립트가 묶음 높이를 --dock-h로). 앨범 칸 이름에서 '정보' 뺌, 아이 여럿·안 골랐으면 한마디 대상 '아이', 화면 읽기 제목을 부품 안으로
  - 2회차: 가족 크게 보기 회귀 확인(영상 막대·저장·반응 e2e), 스크립트 없을 때 묶음 배치
  - 3회차: e2e pview(12개 + 글씨 3단계 × 화면 3개 가림 검사), photo·swiper·reactions·vplay·save 통과. react.py는 dev에서도 실패(심어 둔 가족방에 사진이 없어 첫 하트를 못 찾음 — 테스트 순서 의존, 이번 변경과 무관)
- (라) 사진 정보 수정 화면 완료(feature/photo-edit): 제목 '사진 정보 수정', 닫기 → 크게 보기, 작은 미리보기(10rem), 스와이퍼 걷어냄(넘겨 보기는 크게 보기에서), 저장하면 크게 보기로 + '사진 정보를 저장했어요.' 알약(완료 안내 움직임을 base.css로 옮겨 가족 화면도 씀). 리뷰 3회차
  - 1회차: 남은 /photo 링크 점검 → 알림 목록이 수정 화면으로 가고 있었음 → 크게 보기로. 그런데 크게 보기엔 한마디 글이 없어 알림에서 온 엄빠가 글을 못 봄 → 디자인 121에 최근 한마디 말풍선 넣고(왼쪽, 수정 버튼은 오른쪽) 코드 적용
  - 2회차: 지운 스타일(.sp-p__stage·arrow·track·slide) 참조 없음 확인, 지우기·오류 흐름은 그대로
  - 3회차: e2e photo(수정 흐름·저장 뒤 알약), pview(말풍선 포함), reactions(알림 → 크게 보기 한마디), vplay, save 통과. swiper.py는 사진 정보 스와이퍼를 걷어내서 지움(크게 보기 스와이퍼는 (마)에서 새로)
  - 디자인에 없는 것: 크게 보기 완료 알약은 보드에 상태로 안 그림
- (마) 크게 보기 스와이퍼 완료(feature/viewer-swiper, 엄빠·가족 공통): 서버가 앞뒤 20장 주소를 서명해 넘기고(slideWindow, 창 밖 이웃 before·after), 스크립트가 CSS 스크롤 스냅 트랙으로 바꿈. 멈추면 replaceState + 그 화면을 받아 위 메뉴·아래 판만 갈아 끼움. 영상에 멈추면 그 화면을 새로 엶(재생 막대), 영상 화면 자체는 예전처럼. 스크립트 없으면 한 장 + ‹ › 링크. 리뷰 3회차
  - 1회차(별도 리뷰): 손가락 댄 채 멈추면 중간 위치에서 넘어감 → 칸에 딱 맞을 때만, scrollend 있으면 시간 기다리지 않음. 불러오는 동안 지난 사진 폼이 남아 반응이 지난 사진에 감 → 위 메뉴·아래 판 inert. 빠른 두 번 누르기가 한 칸만 → 가는 중인 칸 기준. 끝에서 › 숨으면 포커스 사라짐 → ‹ 로. 슬라이드 이름 고정·바뀐 사진 안 알림 → 슬라이드마다 이름, 제목 aria-live. 화살표 이름(사진/영상) 갱신. 확대한 채 위아래 둘러보기 막힘 → 트랙 pan-y 추가. 연달아 넘기면 이전 요청 끊음(AbortController)
  - 2회차: e2e vswipe(엄빠·가족 넘기기, 넘긴 사진에 반응, 화살표, 스크립트 없을 때, 빠른 두 번, 포커스, 잠금)·pview·vplay·photo·reactions·save 통과
  - 3회차(기능): 손가락 따라 넘김·페이지 안 부름 충족. 남은 것: 쓰다 만 한마디는 넘기면 지워짐, 영상 쪽 넘기기는 기록이 쌓임(사진은 안 쌓임), 아이폰 실기기(스냅·확대·inert) 확인 필요
- 배포(2026-10-27 07:50, 0.3.0): 실제 DB에 마이그레이션 parent_reactions 적용(사용자 승인) → dev 머지·푸시 → 자동 배포. /view 응답 확인
- 사고: 0.2.6(10-27 00:56, ‹ 뒤로 링크) 배포에 부모 반응 백엔드 코드가 같이 올라감. 원인: fix/back-chevron 브랜치를 DB 작업이 머지된 로컬 dev에서 만든 뒤, dev를 origin으로 되돌리고 그 브랜치를 머지함. 그 사이(약 01:00~07:50) 실제 DB엔 parent_user_id가 없어 사진 정보 화면(최근 한마디 불러오기 parents 연결)이 실패했을 것. 마이그레이션 적용으로 해소. 다음부터: 배포 브랜치는 origin/dev에서 만들고, 푸시 전 origin/dev와의 차이(git diff --stat)를 확인
- 나눠서 머지: (가) 디자인 → (나) DB: 부모 반응·한마디 → (다) 크게 보기 공통 부품 + 엄빠 갤러리 → (라) 사진 정보 수정 화면 → (마) 조부모 크게 보기 스와이퍼. 단계마다 코드 리뷰·검증·기능 리뷰 3회차

### 49. feature/album-masonry — 엄빠 앨범 배열을 디자인대로 (완료, dev 머지)

- 요구사항(사용자 2026-10-27 캡처 + "배열", "디자인대로 개발 진행 안 하는 건 왜야"): 디자인 ParentHome은 2줄 엇갈린 배열(사진 비율대로 높이)인데 코드는 3줄 정사각 격자였음
- 원인: 33번(아이 탭) 때 "칸 모양은 그대로 둠"으로 미뤄 둠. 보드와 화면을 나란히 대조하지 않고 기능 검증만 했음
- 방식: src/lib/masonry.ts(가장 짧은 줄에 쌓기, 단위 테스트) → 서버가 칸마다 줄·시작·칸 수를 CSS 변수로(2줄·4줄 둘 다), CSS 격자 + 컨테이너 단위(cqi)로 높이. 스크립트 없음, DOM은 날짜 순서. 받은 하트·한마디 알약(이름에도 넣음), 영상 길이, 달 제목 '10월'(올해) + '하린 생후 N개월 · 사진 N'
- 리뷰 3회차: 1회차 디자인 보드와 나란히 비교(남은 차이: 오른쪽 위 가족 버튼, 새 반응 하트 올라가는 움직임 → 전체 대조 목록으로), 2회차 접근성(알약은 화면 읽기에서 숨기고 사진 이름에 수), 3회차 e2e masonry(2줄·비율·알약·달 제목·4줄)·photo·kidtabs·parent·pview 통과
- 다음: 모든 화면 디자인 대조 목록 → 차이 고치기. 리뷰 3회차에 '디자인 보드와 화면 비교'를 항상 넣음

### 50. fix/top-button-align — 위 버튼 자리 통일 (완료, dev 머지, 디자인 123)

- 요구사항(사용자 2026-10-27 "사진 정보 수정 닫기와 사진 채워 보기 닫기 위치가 다름, 상단 버튼 위치 다 맞춰"): 
- 원인: 크게 보기(.sp-v__bar)는 가족 화면용 간격(위 16px·옆 12px + 링크 안쪽 8px, 큰 글씨 단위)으로, 엄빠 화면(.sp-p__bar)은 화면 안쪽 여백 20px + 44px 줄로 따로 만들어짐. 디자인 보드도 둘이 달랐음(크게 보기 16/12, 엄빠 화면 20/20)
- 고침: 기준을 엄빠 화면으로(글자 왼쪽 20px, 세로 가운데 46px). 디자인 크게 보기 보드 6개(조부모·영상·엄빠) 먼저 고치고, 코드 .sp-v__bar 위 여백을 46px - 누를 칸 높이/2, 옆 20px, 링크 안쪽 여백 0, 굵기 600(디자인)
- 검수: 재기(topbtn.py) 크게 보기 닫기 (20, 45) · 수정 화면 닫기 (20, 46) · 뒤로 ‹ (20, 46). 디자인과 나란히 캡처(빨간 기준선 x 20·y 46). e2e pview·vswipe·vplay·photo 통과
- 남은 차이(전체 대조 목록에서 같이): 하위 화면 제목은 디자인이 위 줄 가운데 작은 제목, 코드는 아래 큰 제목

### 51. fix/edit-design-emoji — 사진 정보 수정 디자인 대조, 반응 이모지 (완료, dev 머지, 디자인 124)

- 요구사항(사용자 2026-10-27 "이모지 좀 더 줄여, active 시 정렬 안 맞아", 수정 화면 캡처 + "디자인이랑 비교")
- 원인
  - 이모지: 그림은 40px 고정인데 담는 칸은 2.5rem(엄빠 화면은 글자 배율이 작아 약 33px) → 그림이 칸 밖으로 삐져나와 눌림(테두리) 때 어긋나 보임. 밝은 화면에선 버튼 배경(--panel-item 흰 반투명)이 판과 같은 색이라 안 보였음
  - 수정 화면: 큰 제목·따로 놓인 입력칸·말풍선 없음(디자인과 다름), 폼이 flex:1로 늘어나 '사진 지우기'가 멀리 떨어짐
- 고침: 디자인 이모지 28px(보드 10개) → 코드 칸 1.75rem·그림 100%, 버튼 회색 칸. 수정 화면: 위 줄 닫기 + 가운데 작은 제목(.sp-p__nav), 160px 미리보기 + 최근 한마디 말풍선, 찍은 날·아이·그룹 한 묶음 목록(.sp-p__group, 날짜는 줄 오른쪽 초록 글자), 칩 15px, 지우기 저장 바로 아래
- 검수: 디자인과 나란히(ed-cmp.png), 이모지 가운데·그림=칸 크기 재기, e2e editshot·photo·pview·vswipe·reactions·save 통과
- 남은 차이: 크게 보기 '생후 N개월'(가족 쪽은 아이 생일 정보가 없어 DB 필요), 미리보기 하트 올라가는 움직임

### 52. 디자인 대조 — 전부 맞추기 (진행 중)

- 요구사항(사용자 2026-10-27 "큰 차이 말고 개발하고 나면 디자인 검수 함께"): 디자인 보드와 실제 화면 차이를 크기 상관없이 전부 맞춘다. 앞으로 모든 개발은 리뷰 3회차에 디자인 보드와 나란히 캡처 검수를 넣는다
- 목록: design-audit.md(화면별 체크리스트, 54개 비교 이미지). 순서: 공통 패턴(하위 화면 머리글 → 묶음 행 → 콩이 → 시트·모달) → 가족 화면 → 엄빠 화면 → 설정. 묶음마다 브랜치 하나, 리뷰 3회차 + 나란히 캡처 검수 후 머지

### 53. fix/subpage-header — 하위 화면 머리글 (완료, dev 머지)

- 디자인 대조 1번 패턴. 원인: 하위 화면을 '뒤로 줄 + 아래 큰 제목(h1)'으로 만들어 왔음(35번에서 발견하고 미룸)
- 고침: 13개 화면(가족·그룹·그룹 추가·그룹 상세·비밀번호·구성원·문자로 공유·글자 크기·아이·아이 추가/고치기·저장 용량·계정·접종)을 .sp-p__nav(왼쪽 ‹ 이전, 가운데 작은 h1)로. 접종 화면 제목은 '접종·검진', 아이 줄은 h2. 뒤로 글자 보통 굵기(디자인), 구성원 이름 20px
- 검수: subhead.py 14개 화면 — 제목 가운데(±1px)·뒤로와 같은 줄·세로 46px·왼쪽 20px. 나란히 캡처(sub-cmp.png). e2e groups·members·health·settings2·photo·upload 통과

### 54. fix/grouped-rows — 묶음 안 줄 + 바로 적용 (완료, dev 머지)

- 디자인 대조 2번 패턴(글자 크기·아이·그룹 상세)과 '+ 추가' 초록 글자
- 원인: 체크·라디오를 카드 밖 왼쪽에 두고 따로 '저장' 버튼으로 보내게 만들었음. '+ ' 띄어쓰기는 버튼이 flex라 공백이 사라졌음
- 고침: AutoSave 부품(data-autosave 폼은 칸이 바뀌면 바로 보냄, form 속성으로 밖에 둔 칸 포함, 스크립트 없으면 저장 버튼). 묶음 줄(.sp-p__group-row--check/--link), 그룹 이름 회색 채운 칸, 아이 줄 콩이 상자·'고치기', 접종 보기 묶음 안, 라디오 오른쪽, 섹션 이름 작은 회색
- 사고 2(사용자 캡처로 발견): 51번에서 만든 .sp-p__group이 가족 화면 그룹 블록의 기존 class와 겹쳐 0.3.3~0.3.5 가족 화면 그룹 칸 여백이 사라짐 → .sp-p__rows로 바꿈(0.3.6). 오늘 만든 class 전부 중복 정의 점검(남은 중복은 원래 의도된 것)
- 같이 찾은 사고: 51번에서 만든 .sp-p__preview가 글자 크기 화면의 미리보기 class와 겹쳐 그 화면이 깨졌음(0.3.3~0.3.4) → .sp-p__thumbbox로 바꿔 먼저 배포. 다음부터 새 class는 만들기 전에 grep으로 겹침 확인
- 검수: rows.py(라디오 오른쪽·바로 저장·고치기·초록·기본 포함·이름 Enter·주소 보내기 줄·스크립트 없을 때) 11개, 나란히 캡처(b2-cmp.png), e2e settings2·groups·health·kidtabs 통과(저장 버튼 대신 바로 적용으로 고침)
### 55. feature/comment-list — 크게 보기 한마디 목록 (완료, 운영 DB 적용, dev 머지 0.4.0, 디자인 126)

- 요구사항(사용자 2026-10-27): 한마디 두 개인데 크게 보기에 안 보임 → 엄빠·가족 모두 본다. 최근 하나는 늘 보이고 '모두 보기'로 나머지. 한마디 모양을 수정 화면과 같은 말풍선으로
- 원인: 처음 설계가 '가족 화면엔 한마디 수만'(comments 읽기 정책이 쓴 사람·엄빠만). 엄빠 크게 보기는 떠 있는 말풍선 하나만 따로 그렸음
- 구현: DB 함수 sp_media_comments(볼 수 있는 사진이면 승인된 가족·엄빠 한마디 최근 100개, 이름·글·시각·내 것. 쓴 사람 id는 안 내보냄, 표 정책은 그대로). 백엔드 mediaComments(목·Supabase). Viewer 판 안 반응 아래: 회색 말풍선(이름 · 방금/어제) + 네이티브 details '한마디 N개 모두 보기 ›'(펼치면 '접기'). 엄빠 떠 있는 말풍선은 없애고 수정 버튼만. 가족 보냄 안내 '가족 모두 볼 수 있어요'
- 영향 파일: supabase/migrations/20261027000002_media_comments.sql, supabase/tests/rls.sql, src/lib/backend/{types,supabase,mock}.ts, src/components/{Viewer,SayForm}.astro, src/pages/{view,album}/[id].astro, src/styles/family.css
- 리뷰 1(따로 리뷰어): 승인 대기 기기가 공유 묶음 사진의 남 이름·한마디를 봄 → 함수에 '승인된 구성원 또는 부모' 조건, DB 검사 추가(조건 빼면 실패하는 것 확인). 옛 말풍선 CSS를 지우는 스크립트가 엉뚱한 곳을 잡아 블록이 복사됨 → 지움. '대기 중 한마디 안 보임'은 해당 없음(대기는 쓰기부터 막힘)
- 리뷰 2(새 리뷰어): 막는 문제 없음. '모두 보기' 개수를 펼쳐지는 목록 수로, 목 한마디 수를 승인된 사람 것만, 수정 화면 최근 한마디도 같은 목록 함수로(mediaInfo의 따로 부르던 쿼리 없앰)
- 리뷰 3: 전체 변경 다시 읽음. 나란히 캡처(cm-cmp·cm-cmp-d·cm-open-parent). e2e comments·pview·vplay·reactions·photo·groups·health·settings2·editshot·rows, 단위·DB·타입 검사 통과
- 배포 순서: 운영 DB에 함수 먼저(안 그러면 크게 보기·수정 화면이 500) → dev 머지. 적용은 지우님 확인 뒤

### 56. fix/thumb-motion — 세로 사진 미리보기 + 디자인 움직임 (계획)

- 요구사항(사용자 2026-10-27): 사진 정보 수정 미리보기에서 세로 사진이 잘림 → '흐린 배경 + 칸 키우기'(칸 높이 고정 200px쯤, 사진 전체 보이게, 좌우는 같은 사진 흐리게). 디자인에 있는 움직임이 앱에 없음
- 원인: 미리보기 칸 160px 고정 + cover라 세로 사진은 가운데 띠만 남음. 디자인 대조를 정지 캡처로만 해서 움직임(sp-rise 반응 올라감, sp-bubble 말풍선 나타남, sp-pop 하트 톡)을 놓침
- 할 일: 디자인 보드 먼저(ParentPhoto 칸 높이·흐린 배경) → 수정 화면 미리보기, 반응 올라가는 움직임(그 사진에 있는 반응 종류만), 말풍선 나타남, 엄빠 앨범 하트 톡. 레이어 보드 움직임도 대조. 움직임 줄이기 설정이면 끔

### 57. feature/reaction-chips — 반응 한 줄(슬랙처럼) + 한마디 한 줄·시트 (완료, dev 머지 0.4.1, 디자인 129~131)

- 요구사항(사용자 2026-10-27): 판 안에 쌓이는 한마디 말풍선이 보기 싫음 → 한 줄 + 누르면 아래 시트(추천안 동의). 이모지가 너무 큼 → 줄이기. 하트가 위(오른쪽 위)와 반응 줄에 두 번 → 하나로("슬랙처럼 괜찮은 듯")
- 원인: 디자인은 '위 하트 + 반응 4개'인데 앱은 반응 줄에 하트까지 5개라 중복. 이모지는 앱 28px(디자인 22px). 55에서 한마디를 판 안 말풍선으로 쌓아 판이 커짐
- 디자인(129~130): 날짜 줄엔 날짜만. 반응 5개 알약 한 줄(이모지 20px, 높이 44px, 수 있으면 옆에 숫자, 누른 건 초록 테두리·연한 초록). 한마디는 회색 한 줄('이름 글…  말풍선 아이콘 N ›', 말줄임) → 누르면 아래 시트(제목 '한마디 N개', 닫기, 이름·때·글 목록, 아래 입력칸). 크게 보기(가족·엄빠·영상·PC)와 넘겨 보기 카드 같은 반응 줄
- 구현: ReactRow에 수 표시(알약), HeartToggle은 크게 보기·넘겨 보기에서 빠짐. Viewer 한마디: 한 줄 링크(#talk) + dialog 시트(스크립트 있으면 showModal, 없으면 :target으로 보임). 시트는 스와이퍼가 바꾸는 판(dock) 안에 둔다
- 영향 파일: src/components/{ReactRow,Viewer}.astro(HeartToggle 지움), src/pages/album/index.astro, src/styles/family.css, e2e
- 리뷰 1(따로 리뷰어): 스크롤 애니메이션 없는 브라우저(iOS 26 전·파이어폭스)는 넘겨 보기 반응 줄이 원래 숨어 카드 하트만 남아 있었는데 하트를 지워 반응할 곳이 없어짐 → 그 브라우저에서만 카드에 하트 알약 하나. 320px·큰 글씨에서 알약 넘침 → 같은 폭 + 줄바꿈. 한 줄 수 대비 4.48:1 → 진한 초록(디자인 131도). 넘기는 중 연 시트가 멈춤 → 넘기기 전에 닫음. #talk로 펼친 시트 닫기 안 됨, 스크립트 없을 때 입력칸 두 개, 닫기 폭 44px
- 리뷰 2(새 리뷰어): 막는 문제 없음. 카드 하트의 숨은 제목·이름표 없앰(카드마다 반복), 카드 바탕과 같은 색 → 회색 칸, #talk 상태에서 다시 눌러도 그대로
- 리뷰 3: 최종 변경 다시 읽음. 나란히 캡처(chip-cmp·chip-cmp-d·swipe-cmp·cm-swipe-old). e2e comments(옛 브라우저 흉내·320px·스크립트 없음 포함)·reactions·pview·vplay·vswipe·editshot·masonry·photo·family 통과. react.py는 예전부터 시드에 사진이 없어 실패

### 58. feature/layer-motion — 레이어 나타나는 움직임 + 이모지 가끔 다시 (완료, dev 머지 0.4.2, 디자인 132~135)

- 요구사항(사용자 2026-10-27): "레이어 애니메이션 추가하면 안 되나?", "이모지가 애니메이션 되다가 멈추네" → '가끔 다시 움직이기' 고름
- 원인: 레이어는 디자인·앱 둘 다 나타나는 움직임이 없었음(정지 디자인). 신청 레이어 반짝 이모지 움직임은 보드에만 있었음. 반응 이모지는 WCAG 2.2.2(5초 넘는 움직임)를 지키려고 두 번만 움직이게 했었음
- 구현: 레이어 배경 0.2초 어두워짐, 상자 0.92→1.02→1 (0.32초), 반짝 이모지 두 번(base.css). 반응 이모지는 처음 두 번 + 6초마다 한 번씩 차례로(0.4초 간격, family.css *-gap 키프레임). 동작 줄이기면 모두 없음. 이모지 반복은 WCAG 2.2.2와 어긋남을 알리고 사용자가 고름. 닫힐 때 움직임은 폼 이동이라 없음
- 디자인: 레이어 보드 12장에 같은 움직임(132), 이모지 쓰는 보드 28장을 '두 번 + 6초마다'로(133)
- 리뷰 1(따로 리뷰어): 넘겨 보기는 카드마다 반응 줄(숨은 줄 포함 약 250개)이 끝없이 움직여 화면을 계속 다시 그림(배터리) → 6초마다 반복은 1분(10번)까지만. 보드도 같게. 그 밖(레이어 transform 충돌·두 움직임 겹침·키프레임 이름)은 문제 없음
- 리뷰 2·3: 변경 다시 읽음, e2e motion(레이어 움직임 이름·횟수, 이모지 2번+10번, 동작 줄이기)·layers·comments·editshot·reactions·vplay 통과

### 59. fix/sms-empty — 문자로 공유하기 빈 상태 (완료, dev 머지 0.4.3, 디자인 134)

- 요구사항(사용자 2026-10-27 캡처): 빈 상태 문구가 안내문보다 크게 나옴. 맞는 문구라면 크기라도 맞아야
- 원인: 디자인에 빈 상태가 없었고, 앱은 크기 없는 .sp-p__note(본문 17px)로 넣었음. 같은 클래스를 쓰는 알림 빈 문구·로그인 준비 중 문구도 같은 문제. 안내문도 디자인 문구('설치 링크')와 달랐음
- 고침: 디자인 SendSetupEmpty 보드(콩이·'아직 들어온 가족이 없어요'·설명·'가족 링크 보내러 가기'). 앱은 엄빠 앨범 빈 화면 형식(.sp-p__empty)으로, 버튼 폭 가득. .sp-p__note를 안내문과 같은 15px로. 안내문 디자인 문구로
- 검수: smsempty.py(제목·크기 같음·버튼 폭·링크·문구), 나란히 캡처(sms-cmp), reactions·settings2·groups 통과

### 60. fix/emoji-once — 반응 이모지는 크게 보기에서 열 때 한 번 (완료, dev 머지 0.4.4, 디자인 136)

- 요구사항(사용자 2026-10-27): "처음 로드할 때만 한 번", "자세히 보기에서만 움직이면" → 크게 보기에서 열거나 넘길 때 한 번, 넘겨 보기 카드는 멈춤(58의 6초마다 반복을 바꿈)
- 고침: .sp-v__panel 안 이모지만 한 번(스와이퍼가 판을 새로 넣으면 다시 한 번), *-gap 키프레임 지움. WCAG 2.2.2도 다시 지킴. 보드: 크게 보기류는 한 번, GrandHome은 멈춤
- 검수: motion.py(크게 보기 5개 한 번씩), comments.py(넘겨 보기 카드 멈춤, 넘긴 사진에서 다시 한 번), vplay·editshot·reactions·layers 통과

### 61. fix/sheet-ios — 아이폰 사파리에서 한마디 시트 목록이 안 보임 (완료, dev 머지 0.4.5)

- 증상(사용자 2026-10-27 아이폰 사파리 캡처): 시트는 열리고 제목·입력칸은 보이는데 한마디 목록이 없음, '닫기'에 네모 초점 테두리
- 원인: 목록이 flex: 1(0%에서 시작)인데 시트 높이는 max-height만 있어 사파리가 목록 높이를 0으로 계산(크롬은 내용 높이). 테두리는 showModal이 첫 초점 대상(닫기 링크)에 초점을 줘서
- 고침: 목록 flex: 0 1 auto(내용 높이에서 시작해 72% 안에서 줄고 굴러감). 시트 제목에 tabindex=-1 autofocus로 초점(화면 읽기는 제목부터, 테두리 없음)
- 검수: sheetios.py(목록 높이, 초점 제목, 12개면 72% 안에서 목록만 굴러감·입력칸 보임), comments.py 통과. 웹킷은 이 환경에 없어 실제 아이폰 확인 필요

### 62. fix/masonry-gap — 엄빠 앨범 사진 사이 세로 간격 = 가로 4px (완료, dev 머지 0.4.6)

- 요구사항(사용자 2026-10-27): 마소니 간격 상하·좌우 같게, 지금 상하가 안 맞음
- 원인: 세로 간격을 높이 단위 1칸(줄 폭의 1/40)으로 비워 화면 폭 따라 4.1~6.9px, 가로는 4px 고정(디자인은 둘 다 4px)
- 고침: 칸 아래 여백을 4px로(차지한 줄은 그대로, 남는 1px 안쪽은 사진이 가짐)
- 검수: gaps.py(375·390·430·1280px에서 세로·가로 모두 4px), masonry.py 통과
### 63. fix/thumb-tall — 사진 정보 수정 미리보기 세로 사진 (완료, dev 머지 0.4.7, 디자인 127)

- 요구사항(사용자 2026-10-27): 세로 긴 사진이 미리보기에서 잘림 → '흐린 배경 + 칸 키우기'
- 원인: 칸 160px 고정 + cover라 세로 사진은 가운데 띠만 남음
- 고침: 칸 200px, 사진은 크기만큼(최대 칸) 가운데·그림자, 남는 곳은 같은 사진을 흐리게(칸보다 40px씩 크게 깔아 가장자리까지), 모서리 isolation. 영상은 포스터로 흐림
- 리뷰 1(따로 리뷰어): 흐림 가장자리 옅은 띠 → 크게 깔기, 파노라마 그림자 → 폭·높이 둘 다 최대로 맞춤(flex 가운데), 옛 사파리 모서리 → isolation
- 리뷰 2·3: 세로·파노라마 측정(thumbtall.py), photo·editshot 통과, 나란히 캡처(thumb-3)

### 64. feature/comment-delete — 한마디 지우기, 쓴 사람만 (완료, 운영 DB 적용, dev 머지 0.4.8, 디자인 137)

- 요구사항(사용자 2026-10-27): 댓글 삭제 기능, 권한은 '쓴 사람만'(엄빠도 남의 것은 못 지움)
- 원인/현재: DB sp_delete_comment가 이미 있었지만 화면이 없었고, 엄빠는 가족방 사진의 모든 한마디를 지울 수 있게 되어 있었음
- 구현: 마이그레이션 20261027000003(sp_delete_comment 쓴 사람만, sp_media_comments에 id). 백엔드 deleteComment(목은 지운 표시로 남겨 하루 한도엔 셈). 시트 안 내 한마디에 '지우기'(이름 줄 오른쪽, 44px) → 네이티브 details로 '이 한마디를 지울까요? [지우기]' → 폼(del) → 지운 뒤 #talk로 돌아와 시트를 모달로 다시 열고 '한마디를 지웠어요.', 다 지웠으면 화면 안내
- 사고: CSS 넣을 자리를 '.sp-v__sheet-form {'로 찾았는데 ':target .sp-v__sheet-form {'이 먼저 걸려 규칙 중간에 끼워 넣음(테스트로 발견, 바로잡음). 앞으로 자리 찾기는 줄 처음(^)으로 고정
- 운영 DB 적용은 지우님 확인 뒤(머지 전에 적용해야 함: 새 코드가 목록 id를 씀)
- 운영 적용: drop function이 든 마이그레이션은 도구가 '취소됨'으로 두 번 돌아옴(파괴적 작업 확인이 전달 안 됨) → drop 없이 id 돌려주는 새 함수 sp_comment_list를 만들고 옛 sp_media_comments는 남김(다음 정리 때 지움). 적용 뒤 함수 결과·권한·엄빠 조건 빠짐 확인
- 리뷰 1(따로 리뷰어): 보안·마이그레이션 문제 없음(checkOrigin, back 제한 그대로). 고침: 지운 뒤 #talk로 돌아와 모달을 닫으면 :target 때문에 판 안에 다시 펼쳐짐 → #talk 대신 서버가 시트를 open으로 그리고 스크립트가 모달로 바꿈(스크립트 없으면 판 안에 펼침), 주소에서 say 뗌. 지우기 실패 안내(delerror) 없었음 → 시트 안에 '지우지 못했어요'. 안내를 시트 설명(aria-describedby)으로. 목의 '내 것'을 DB처럼 활성 기기·승인된 구성원으로. 지우기 누를 자리를 이름 줄 쪽으로. DB 검사에 다른 가족·다른 집 부모 거부 추가(61건)
- 리뷰 2(새 리뷰어): :modal을 모르는 옛 브라우저(iOS 15.4~15.5 등)에서 스크립트가 멈추고 CSS 규칙(:target 펼침 포함)이 통째로 무시됨 → :modal 대신 서버가 붙인 sp-v__sheet--inline 클래스, 시트 바로 뒤 인라인 스크립트가 첫 화면 전에 모달로(깜빡임 없음), 다 지운 경우에도 주소에서 say 뗌, 안내 role=status 중복 뗌
- 리뷰 3: cdelete(지우기·재열림·닫으면 사라짐·실패 안내·엄빠 못 지움·다 지움·스크립트 없음)·comments·sheetios·reactions·pview·vplay·vswipe·photo·editshot·motion, 단위·DB(61) 통과, 디자인 대조(del-cmp)

### 65. fix/delete-icon — 한마디 지우기를 휴지통 아이콘으로, 자리 바로잡기 (완료, dev 머지 0.4.9, 디자인 138)

- 요구사항(사용자 2026-10-27): 지우기 위치 확인, '지우기' 글자 대신 삭제 아이콘
- 원인: 리뷰 1회차에서 누를 자리를 위로 올리며 기준을 li 바깥(top:-12px)으로 잡아 이름 줄보다 위에 뜸. 다시 연 시트 제목 테두리는 전체 .sp-body :focus-visible 규칙이 이겨서
- 고침: 휴지통 아이콘(20px, 누를 자리 44px, 이름 '한마디 지우기: 글'), 이름 줄 가운데·오른쪽 끝(디자인과 같은 2px 안쪽). 제목 초점 테두리 규칙을 더 구체적으로
- 검수: cdelete(아이콘 자리·이름·제목 테두리 없음 포함)·comments·sheetios 통과, 나란히 캡처(del-cmp2)

### 66. fix/toast — 한마디 결과·저장 안내를 디자인 토스트로 (완료, dev 머지 0.4.10, 디자인 139)

- 요구사항(사용자 2026-10-27 캡처): '한마디를 써 주세요' 같은 안내를 토스트 디자인에 맞춰, 왜 안 없어지나
- 원인: 한마디 결과는 입력칸 아래 고정 상자(.sp-f__box)라 계속 남고 판이 길어짐, 주소의 say=로 새로 고침해도 다시 뜸. 저장 안내는 위쪽 알약(.sp-v__toast)으로 모양이 또 달랐음
- 고침: Toast 부품(디자인 GrandHome 카드: 반투명, 18px 모서리, 60px, 보냄=하트+반짝 role=status 4초, 오류=빨간 느낌표 role=alert 6초), 크게 보기에선 판 바로 위 12px, 넘겨 보기는 화면 아래. 문구는 lib/say. 크게 보기 스크립트가 주소에서 say·sm 뗌. 동작 줄이기면 움직임 없이 사라짐. 오류 토스트 디자인 보드 ToastError, 크게 보기 보냄 ToastSent 추가
- 검수: toast.py(오류·보냄·판 위 12px·4/6초 뒤 사라짐·새로 고침·동작 줄이기), vplay·photo·pview·comments·cdelete·sheetios 통과, 나란히 캡처(toast-cmp)

### 67. feature/instant-actions — 크게 보기 누르기·페이지 넘김 빠르게 (완료, dev 머지 0.4.11, 디자인 140)

- 원인(사용자 "너무 느린데", "페이지 전환 쓰레기"): 하트·반응·한마디·지우기가 모두 폼 POST → 같은 페이지로 이동 → 전체 다시 그리기. 누를 때마다 하얗게 깜빡이고 판·스크롤이 처음으로
- 구현: 크게 보기 스크립트가 `.sp-v__more` 안 폼 제출을 가로채 fetch(같은 폼 데이터+누른 버튼) → 돌아온 페이지에서 `.sp-v__more`와 토스트만 갈아 끼움. 반응은 누르는 즉시 눌림·수를 바꿔 두고(낙관적), 요청은 차례로 보냄. 실패하면 페이지를 새로 엶. 넘기는 중 바뀐 사진이면 버림. 시트가 열려 있었거나 지운 뒤(서버가 open으로 그림)면 새 시트를 showModal
- 페이지 이동: base.css `@view-transition { navigation: auto }`(움직임 줄이기면 끔) — 하얀 깜빡임 대신 겹쳐 넘어감. 지원 안 하는 브라우저는 지금과 같음
- 스크립트 없으면 지금처럼 폼 POST. 화면 모양 변경 없음(디자인 캔버스 변경 없음)
- 영향 파일: src/components/Viewer.astro, src/styles/base.css
- 리뷰 3회 반영: 보낸 글 즉시 비움(되살아나 두 번 보내기 방지)·실패하면 글 돌려줌, 건너뛴 응답의 안내도 띄움(다른 사진 것은 버림), 쓰던 칸·커서 유지, 판 밖 포커스는 안 건드림, 큐 예외 뒤 새로 열기, 늘 있는 알림 칸(status·alert)에 글자만 넣어 읽기, 시트가 열려 있으면 안내·알림 칸을 시트 입력칸 위로(디자인 CommentSheetToast 추가)
- 엄빠 크게 보기: 목록·반응·한마디를 한 번에(Promise.all) 받음
- 시트에서 보내면 시트가 열린 채 남음(전에는 페이지가 새로 열려 닫혔음)
- 미리 받기(prefetch)는 뺌: GET에 부작용 있는 주소(/m, /auth, 로그아웃 등)와 서버 부담 때문에 따로 판단

### 68. fix/delete-toast — 토스트 아이콘 빼기·지운 안내도 토스트·페이지 전환 오류 (완료, dev 머지 0.4.12, 디자인 141)

- 사용자: "한마디를 지웠어요는 왜 또 저렇게 뜰까", "토스트 아이콘 빼줘", 콘솔 'ViewTransition opt-in disabled'
- 원인: 지운 안내만 시트 안 초록 박스(sp-v__sheet-note)로 남아 있었음(시트가 토스트를 가려서). 이제 시트 안 입력칸 위에 토스트를 띄울 수 있음
- 토스트: 하트·반짝·느낌표 아이콘 없이 글자만(디자인 GrandHome·ToastSent·ToastError·CommentSheetToast 고침). 오류와 보냄은 화면 읽기(alert/status)로만 구분
- 지운 안내·실패 안내: 페이지 토스트로 그리고, 시트가 열리면 시트 입력칸 위로 옮김(인라인 스크립트·즉시 반영 둘 다). 토스트 글자 칸 id=talk-note로 시트 설명 연결. 디자인 CommentSheetDeleted 추가
- 페이지 전환: @view-transition을 @media 밖 맨 위로, 움직임 줄이기는 애니메이션만 끔. 사용자 오류는 여기서 재현 못 함(헤드리스 크롬) — 실기기 확인 필요
- 영향 파일: Toast.astro, Viewer.astro, family.css, base.css

### 69. fix/sheet-toast-pos — 시트 토스트가 한마디를 가림 (완료, dev 머지 0.4.13, 디자인 142)

- 사용자: "댓글창에서 토스트가 뜨면서 가리는 현상"
- 시트가 열려 있으면 토스트를 시트 위쪽 바깥(어두운 곳)에 12px 띄움. 시트는 overflow: visible(목록은 따로 굴러감). 디자인 CommentSheetToast·Deleted도 같은 자리로

### 70. feature/photo-delete-layer — 사진 지우기를 레이어로 (완료, dev 머지 0.4.14, 디자인 142 PhotoDeleteLayer)

- 사용자: "사진 지우기도 레이어로 띄워줘 / 이 사진을 지울까요?"
- 스크립트 있으면 '사진 지우기' 링크가 dialog#del을 showModal(주소·화면 그대로). 취소는 form method=dialog(브라우저 기본), Esc·바깥 누르면 닫힘, 포커스는 취소에서 시작
- 스크립트 없으면 ?confirm=delete로 같은 레이어를 연 채 다시 그림(홈 레이어와 같은 .sp-layer 구조). 예전 경고 카드는 없앰
- base.css .sp-layer__modal(가운데·바깥 어둡게·닫혀 있으면 숨김)


### 71. feature/family-inplace — 설정 › 가족 그 자리에서 (완료, dev 머지 0.4.17, 디자인 144)

- 요구사항(다음 할 일 1-1): 승인·거절·내 가족 아님·링크 만들기를 페이지 이동 없이 그 자리에서. 거절·내 가족 아님 확인은 가운데 레이어. 결과 안내는 토스트. 스크립트 없으면 지금처럼 폼
- 디자인: FamilyRejectLayer·FamilyRevokeLayer(가운데 레이어, 빨강 버튼·취소), FamilyApprovedToast(탭바 위 12px 토스트) 추가
- 구현
  - 토스트(`Toast.astro`) CSS를 family.css → base.css로(엄빠·가족 공통), 엄빠 탭 화면은 탭바 위(parent.css)
  - `/settings/family`: 결과 안내를 Toast로(오류도 토스트), 서버 확인 카드(`?confirm=`)를 `.sp-layer` 레이어로(사진 지우기와 같은 구조)
  - 스크립트: 거절·내 가족 아님 버튼은 `dialog.sp-layer__modal`을 열고(취소는 `formmethod="dialog"`), 이 화면 폼 제출은 fetch로 보내 돌아온 화면의 내용(`main`)과 탭 배지만 갈아 끼움. 차례로 보내기, 안내는 늘 있는 알림 칸으로 읽기, 실패하면 오류 토스트
- 영향 파일: `src/pages/settings/family/index.astro`, `src/styles/base.css`, `src/styles/family.css`, `src/styles/parent.css`, `tools/design/familylayer.py`, `tools/e2e/famplace.py`
- 예상 결과: 누르면 하얗게 깜빡이지 않고 카드가 빠지거나 링크 카드가 생기며 토스트. 스크립트 끄면 지금처럼 동작
- 리뷰 3회 반영: 타입 오류(Worker 타입의 Element.prepend와 겹침 → insertBefore), 열린 확인 레이어는 갈아 끼우기에서 뺌, `?confirm=`으로 온 확인도 모달로(취소·Esc면 원래 화면), 스크립트 없을 때 결과 토스트에 초점(Toast `focus`), 다시 만들기 뒤 링크 카드로 초점, 실패하면 누른 버튼으로 초점·건너뛴 성공 화면 먼저 그림, 연 버튼이 바뀌었으면 새 버튼으로 초점
- 검사: `tools/e2e/famplace.py`(28개, 스크립트 있음·없음), family·members·groups·layers·badge·toast·instant 통과. 검사 도우미 layerfix는 확인 레이어(#confirm)를 건드리지 않음
- 주의: `tools/dev.sh`·대부분 e2e 파일 경로가 `/home/claude/sweepea`로 박혀 있음 → 다른 컴퓨터에선 경로를 바꿔 실행(famplace.py는 상대 경로)
- 디자인과 다른 점(이번 범위 밖, 그대로 둠): 새 기기 줄(디자인은 한 줄 + '내 가족 아님'만, 코드는 카드 + 승인 버튼), 그룹 목록(디자인은 그룹 상세로 가는 줄, 코드는 '링크 만들기' + 들어온 사람 목록)

### 72. fix/emoji-native — 반응 이모지를 기기 기본 이모지로 (완료, dev 머지 0.4.16, 디자인 145)

- 사용자: "아이콘 도트 느낌 말고 그냥 이모지로, 기본 이모지로"
- 하트 ❤️·최고 👍·좋아 😊·감동 😭·반짝 ✨. 감동은 🥹 대신 😭(옛 폰·카톡 웹뷰에서 네모로 안 깨지게, 도트 그림도 눈물 흐르는 얼굴)
- `src/lib/emoji.ts` 도트 svg·sprite 없앰 → 글자, `ReactRow`·홈 레이어 반짝은 글자로, 토큰 `--emoji-font`(애플·윈도·노토 컬러 이모지). 움직임은 그대로
- 디자인: 도트 svg가 있던 보드 30개(116곳)를 같은 크기 이모지 글자로(`tools/design/emoji.py`)

### 73. feature/photo-save-inplace — 사진 정보 수정 저장 그 자리에서 (완료, dev 머지 0.4.18, 디자인 146 PhotoSavedToast)

- 요구사항(다음 할 일 1-2): 저장해도 크게 보기로 넘어가지 않고 이 화면 그대로 "저장했어요." 토스트(탭바 위 12px). 스크립트 없으면 지금처럼 크게 보기로
- 구현: 저장 폼을 `x-sp-inplace: 1` 헤더로 fetch → 서버는 저장되면 204(크게 보기를 그리지 않음), 고칠 게 있으면 이 화면을 다시 그려 폼만 갈아 끼우고 고칠 칸으로 초점, 로그인 끝남 등 다른 화면이면 그 화면으로, 실패하면 오류 토스트. 결과는 늘 있는 알림 칸(#ph-live·#ph-urgent)으로 읽기, 두 번 눌러도 한 번 보냄, 누르는 동안 빠진 초점은 저장 버튼으로. 화면 안 결과 안내(`?done=error`)도 Toast(`focus`)로, `?done=`은 떼어 새로 고침해도 다시 안 뜸
- 리뷰 반영: 처음엔 크게 보기 화면 주소로 성공을 판단했는데, 오래된 사진(최근 200장 밖)·고른 아이에서 뺀 사진은 크게 보기가 /home으로 보내 저장돼도 화면이 넘어가고 안내가 없었음 → 서버가 204로 바로 알림. 서버 저장 실패로 다시 그려지면 초점은 저장 버튼으로
- 검사: `tools/e2e/photosave.py`(12개, 스크립트 있음·없음·서버 204/303), photo·pview·photodel·editshot 통과. photo.py의 지우기 단계(옛 #confirm)와 editshot의 반응 그림 측정(옛 도트 svg)은 예전 변경 때부터 깨져 있던 것을 같이 고침

### 74. feature/home-layer-inplace — 홈 가운데 레이어 그 자리에서 (완료, dev 머지 0.4.19, 디자인 변경 없음)

- 요구사항(다음 할 일 1-3): 닫기·나중에는 그 자리에서 닫히고, 다른 화면 가는 버튼(확인하기·사진 올리기·저장 용량 보기)만 이동
- 구현: 스크립트가 레이어를 모달(showModal, `.sp-layer__modal`)로 올림 → Esc·초점 가두기. 닫기·나중에·Esc는 바로 닫고 봤음을 뒤에서 적음(`x-sp-inplace` + keepalive, 서버 204). 레이어는 한 번에 하나(들어오기 신청 → 백일/생일 → 저장 공간): 뒤 것은 서버가 숨겨(hidden) 그려 두고 앞 것을 닫으면 이어서 띄움(전에는 다음에 열 때). 다 닫으면 화면 제목으로 초점. 스크립트 없거나 dialog 모달을 모르는 옛 브라우저는 그대로 폼
- 같이 고침: 레이어 여러 개일 때 id(layer-t·layer-d) 겹침 → join-·day-·storage-
- 리뷰 3회: 대기 레이어가 열린 채 아래 깔림(→ 차례 전엔 숨김), 옛 브라우저에서 숨기기만 하고 멈춤(→ 지원 확인 먼저), 사파리 15.4~15.6 Esc(requestSubmit 없음 → click)
- 검사: `tools/e2e/homelayer.py`(14개), layers·layers45(날짜를 오늘 기준으로 고침, 저장 공간은 `SWEEPEA_MOCK_USED_BYTES=4939212390`로 띄운 서버에서)·badge·family·members·install·groups·photo 통과. layerfix는 숨긴 레이어 건너뛰고 이어 뜨는 레이어도 닫음

### 75. feature/member-inplace — 가족 한 명 그 자리에서 (완료, dev 머지 0.4.20, 디자인 148 MemberRemoveLayer·MemberUploadToast)

- 요구사항(다음 할 일 1-4): 사진 올리기 허용 스위치는 그 자리에서 + 토스트, 내보내기 확인은 레이어
- 구현: 스위치는 누르는 즉시 바꿔 두고 fetch → 돌아온 화면의 `.sp-p`·탭바만 갈아 끼움(가족 화면과 같은 방식, 차례로 보내기·마지막 응답만 그림). 실패하면 마지막 서버 상태로 되돌리고 오류 토스트. 내보내기는 이 화면 위 `dialog#mem-ask`(모달) → 내보내면 설정 > 가족으로 이동해 결과 토스트. 결과 안내는 Toast(`focus`), `?done=` 뗌. 스크립트 없으면 예전처럼(스위치 폼, 내보내기 → 설정 > 가족 확인 레이어)
- 리뷰 3회: 연달아 실패하면 스위치가 서버와 반대로 남음(→ 서버 상태 기억, 그리지 않은 응답에서도 읽음), 화면이 바뀐 뒤 레이어 닫으면 초점 사라짐(→ 새 버튼으로)
- 검사: `tools/e2e/memberplace.py`(20개), members·famplace(다른 화면에서 온 ?confirm= 모달은 주소로 직접 열어 검사)·family·groups·badge·settings2 통과
- 확인 필요: 헤드리스 스크립트 없는 검사에서 페이지 이동 직후 잠깐 `<html>`이 누르기를 가로챔(겹쳐 넘어가기 움직임으로 보임, 0.6초 기다리면 됨). 실기기에서 스크립트 꺼진 경우는 드물어 그대로 둠

### 76. feature/autosave-inplace — 바로 저장 화면들 그 자리에서 (완료, dev 머지 0.4.21, 디자인 149 Settings·TextSize·ChildHealth·GroupSaved 토스트)

- 요구사항(다음 할 일 1-5 일부): 설정 첫 화면 '가족도 사진 저장하기' 스위치, 글자 크기, 아이(접종·검진 보기), 그룹(이름·새 사진 기본 포함)을 페이지 이동 없이 + 토스트
- 구현: 공용 부품 `AutoSave`를 고침(새 부품 없음) — data-autosave 폼 제출을 fetch → 돌아온 화면의 `.sp-p`·탭바만 갈아 끼움, 알림 칸 #as-live·#as-urgent, 하던 칸으로 초점(스위치 → id → 이름+값), 고칠 곳 있으면 그 칸으로·바로 읽기, 차례로 보내기·마지막 응답만 그림, 실패하면 그리지 않은 성공 응답이나 다시 받은 화면으로 되돌리고 오류 토스트. 설정 첫 화면 스위치 폼에 data-autosave. 4개 화면 결과 안내를 Toast(`focus`)로. 스크립트 없으면 저장 버튼
- 리뷰 3회: 고칠 곳 안내를 차분한 칸으로 읽음(→ 바로 읽는 칸), 응답 기다리는 동안 이어 쓰던 글이 지워짐(→ 글·커서 옮김), 스위치 초점 못 찾음, 이름 칸 Enter가 두 번 보냄(change + 기본 제출 → 같은 내용은 겹쳐 안 보냄)
- 검사: `tools/e2e/autosave.py`(20개), settings2·rows·groups·health·members·subhead·chev·kidtabs 통과(옛 검사의 ?done= 기다리기를 알림 칸 기다리기로)

### 77. feature/group-layer — 그룹 주소 보내기·다시 만들기 그룹 화면에서 (완료, dev 머지 0.4.22, 디자인 150 GroupLinkCard·GroupResetLayer)

- 요구사항(다음 할 일 1-5b): '주소 카톡으로 보내기'·'주소 다시 만들기'가 설정 > 가족으로 넘어가지 않고 그룹 화면에서. 다시 만들기는 확인 레이어
- 구현: 서버 변경 없음 — 그룹 화면 스크립트가 /settings/family로 보내고 돌아온 화면의 링크 카드(#link)를 가져와 목록 아래에 붙이고 제목으로 초점. 다시 만들기는 이 화면 `dialog#grp-ask`(모달). 실패하면 그 화면 토스트나 오류 토스트. 스크립트 없으면 예전처럼 설정 > 가족으로
- AutoSave 보강: 다시 그린 뒤 `autosave:drawn` 알림(초점 찾기 전에, 그 자리에 붙인 링크 카드를 다시 붙이게), 열려 있는 `dialog[data-autosave-keep]`은 건드리지 않음(옮기면 모달이 풀림)
- 리뷰 3회: 이름 저장 응답에 열린 확인 레이어가 사라짐(→ keep), 링크 카드 안 초점 사라짐(→ 알림 먼저), 만드는 중 확인 레이어가 안 닫힘
- 검사: `tools/e2e/groupplace.py`(12개), groups·rows·members·settings2·autosave·famplace 통과

### 78. feature/savebar — 저장 버튼 아래 고정 + 접종 바로 저장 (완료, dev 머지 0.4.23, 디자인 151)

- 요구사항: 접종 체크 저장 버튼이 맨 아래라 찾기 힘듦(사용자), 저장 같은 아래 버튼은 아래 고정(사용자 제안), 다음 할 일 1-5c
- 디자인: 접종 보드는 원래 '체크하면 완료한 날짜가 기록돼요'(저장 버튼 없음) → 디자인대로 체크하면 바로 저장 + 토스트(HealthSavedToast). 입력 화면(ChildAdd·PasswordChange·ParentPhoto와 그 레이어·토스트 보드)은 저장 버튼을 탭바 위 막대로. ChildAdd·PasswordChange 보드에 남아 있던 도트 이모지도 기본 이모지로
- 구현: `.sp-p__savebar`(탭바 위 고정 막대, 넓은 화면은 맨 아래), Parent `savebar` → `sp-p--savebar`(막대 높이 `--savebar-h` rem만큼 아래 여백, 토스트는 막대 위 12px). 적용: 사진 정보 수정·아이 고치기/추가·그룹 추가·그룹 비밀번호. 접종은 AutoSave(data-autosave) + 바꾼 칸만 보내기(`toggle=키:on|off`, 스크립트 없으면 예전처럼 저장 버튼·전체 폼). AutoSave는 펼친 `details[id]` 유지
- 리뷰 3회: 체크했다 바로 풀면 완료로 남음(→ 바꾼 칸만 보내기, 폼이 새것이 되면 놓치던 것도 고침), 막대 높이 px 고정(→ rem), `:has()` 없는 브라우저(→ 레이아웃 표시), 토스트 자리가 탭바 규칙에 덮임(→ 우선순위)
- 검사: `tools/e2e/savebar.py`(22개, 지연 600ms에서 체크 후 바로 풀기, 글자 24px), health·photo·photosave·settings2·groups·editshot·autosave·groupplace 통과

### 79. feature/video-multipart — 큰 영상 나눠 올리기 (완료, dev 머지 0.4.24, 화면 모양 변경 없음)

- 원인(사용자 "영상 4개 크다고 안 올라갔네"): 영상 원본을 Worker로 보내는데 Worker 요청 한도가 100MB라 100MB 넘는 영상은 고를 때 빠졌음
- 구현: `api/media/[id]/multipart`(R2 multipart: 만들기 → 50MB 조각 PUT → 합치기, 그만두면 abort). 한 편 2GB·조각 41개까지(`BIG_VIDEO`). 올리기 화면은 90MB 넘는 영상만 이 길로(조각마다 두 번까지 다시), '올리는 중… n / 전체 · 영상 38%'. 합친 키는 지금처럼 done으로
- 리뷰 3회: 2GB 영상으로 5GB 한도를 크게 넘길 수 있음(→ 완료 때도 한도, 마이그레이션 `20261027000004_finish_quota.sql` + mock, 거절되면 올린 파일 바로 지움), 조각 번호 제한(→ 41), 동시에 완료하면 한도를 넘을 수 있음(→ 확인과 더하기를 한 문장으로, 넘으면 예외로 함께 되돌림)
- 검사: `tools/e2e/bigvideo.py`(12개, 재생되는 130MB 파일 → 조각 3개·재생·용량·API 거절), upload, 단위 24, DB(PG18에서, 의도한 거부 62건 — run.sh를 macOS bash에서도 돌게, `LANG=C LC_ALL=C PG_BIN=/opt/homebrew/opt/postgresql@18/bin npm run test:db`)
- 남은 것(사용자): 운영 DB에 마이그레이션 적용 확인, R2 버킷 `sweepea-media`에 '끝나지 않은 multipart는 1일 뒤 중단' 수명 주기 규칙 확인·추가(여기선 Cloudflare 로그인이 없어 못 봄. 끝내지 않은 조각은 목록에 안 나와 매일 정리 작업이 못 지움)
- 같이 발견(이번과 무관, dev에서도 실패): upscreen.py 'EXIF 찍은 날로 월 묶음', vplay.py '한마디 보냄 토스트'. 다음에 원인 확인

### 80. feature/video-shrink — 영상은 폰에서 1080p로 줄여 올리기 (완료, dev 머지 0.4.25, 디자인 152~154)

- 요구사항(사용자 2026-10-27 "네 추천대로"): 영상도 사진처럼 올리기 전에 폰에서 줄인다. 무료는 줄인 사본만 올림(원본은 부모 폰에 남음, 서버 원본 보관은 유료로 나중). 3일 원본 보관·서버 변환은 하지 않기로
- 근거: 아이폰(iOS 18.7) 시험 화면에서 4K 22초 96MB → 720p 6.6MB, 46초(영상 길이의 2배). 1080p도 시간은 비슷(원본 푸는 데 걸림) → 화질 좋은 1080p(5Mbps). 서버 변환(Cloud Run·Containers·Stream)은 비용·구성이 들어 뺌
- 구현: `src/pages/upload.astro` video()에서 mediabunny(WebCodecs)로 짧은 변 1080·H.264 5Mbps·소리는 AAC로(같으면 그대로) mp4로 바꾼다. 이미 작으면(짧은 변 1080 이하이고 초당 6Mbps 이하) 그대로. 브라우저가 못 하거나 실패·트랙이 빠지면 원본 그대로(지금처럼 큰 것은 나눠 올리기). 줄이는 동안 상태 칸 '영상 줄이는 중… 2 / 3 · 40%' + '다 줄일 때까지 이 화면을 켜 두세요', 화면 꺼짐 막기(되면). 라이브러리는 영상을 골랐을 때만 불러온다
- 영향받는 파일: `package.json`·`package-lock.json`(mediabunny), `src/pages/upload.astro`, `src/styles/parent.css`(필요하면), `tools/e2e/shrink.py`(새), `index.md`, `plan.md`
- 예상 결과: 4K 1분 영상이 약 38MB로 올라가고 앨범에서 재생됨. 저장 용량도 줄인 크기로
- 범위 밖: 유료 원본 보관·원본 다시 올리기(결제 붙일 때), 줄이기 멈추기 버튼, 올리기 화면 전체 개편(대기열 B)
- 범위 추가(사용자, 작업 중): 사진 올릴 때도 퍼센트, 줄이기·올리기 둘 다 진행 막대(네이티브 progress, 퍼센트는 묶음 전체 기준), 원본·압축 안내('스위피는 원본을 따로 보관하지 않으니 원본은 폰에서 지우지 마세요', 크기 칸 아래 늘 보임). 보드 UploadShrink·UploadSending
- 구현 결과: 3분(약 110MB) 넘는 영상은 원본 그대로(줄인 영상을 메모리에 통째로 둠, shortcut 주석). 줄이는 동안 영상 칸 비움·input.dispose, 멈추면(영상 길이 3배·최소 1분 진행 없음) 원본으로, 줄이기·올리기 동안 화면 꺼짐 막기(다른 앱에 다녀오면 다시), 상태 글은 10% 단위로만 바꿔 화면 읽기가 계속 읽지 않게, 고르기 칸은 바쁠 때 흐리게. 라이브러리(약 690KB)는 영상을 골랐을 때만 불러옴
- 리뷰 3회: 긴 영상 메모리(→ 3분 상한), 화면 읽기 소음(→ 10% 단위), 원본 안내가 원본을 올릴 때 틀림(→ '줄일 수 없으면 그대로'·'따로 보관하지 않으니'), 서버에 적는 크기 ±2px(→ 가로세로 둘 다 지정), 올리는 동안 화면 꺼짐(→ 올리기에도 화면 켜기), 영상이 메모리에 두 벌(→ 영상 칸 비움), 멈춤 감시가 잘못 끊음(→ 넉넉히·돌아오면 다시 셈), 쉴 때 빈 칸(→ 막대 감싸개 숨김)
- 검사: `tools/e2e/shrink.py`(21개, ffmpeg로 만든 세로 회전 H.264+AAC 2560x1440 → 1080x1920 h264·aac·재생, 작은 영상 원본, 줄이기 없는 브라우저·H.264 못 만드는 브라우저는 원본), bigvideo(줄이기 끈 브라우저로 나눠 올리기), editshot, 단위 24, astro check 0
- 아이폰 시험 결과(사용자): iOS 18.7, 4K 22초 96MB → 720p 6.6MB 46초, 1080p도 시간 비슷
- 같이 발견: upload.py '처음엔 0장'은 mock 고정 가족에 사진이 이미 있어 실패(서버 API 검사라 이번 화면 변경과 무관, 다음에 확인)

### 81. fix/upload-grid-gap — 올리기 사진 칸 간격 (완료, dev 머지 0.4.26)

- 원인(사용자 "사진 사이 여백 조정", "좌우 상하 달라"): 칸 안 버튼이 줄 안 요소라 칸마다 아래에 글자 여백 5px가 붙어 좌우 4px·상하 9px
- 고침: `.sp-p__upbtn`을 block으로 → 좌우·상하 4px(디자인 보드와 같음). 다른 정사각형 칸(앨범·레이어 썸네일)은 이미 block
- 검사: `tools/e2e/upgrid.py`(폰 4칸·PC 6칸, 고치기 전엔 실패)

### 82. fix/upload-percent — 진행 글은 분수만 (완료, dev 머지 0.4.27, 디자인 155)

- 요구(사용자 "사진 업로드에서 퍼센트 빼줘, 그냥 나눈 숫자 같아", "퍼센트만 빼고 분수는 두고"): 사진은 '올리는 중… 3 / 12'처럼 분수만. 퍼센트는 영상 하나의 진행일 때만('영상 줄이는 중… 1 / 3 · 40%', 큰 영상 나눠 올리기 '올리는 중… 1 / 2 · 영상 40%'). 진행 막대는 그대로(묶음 전체 기준)
- 검사: shrink(분수만·막대 중간값), bigvideo(영상 퍼센트), upgrid 통과

### 83. feature/upload-status — 올리기 파일별 상태·못 올린 안내 (완료, dev 머지 0.4.28, 디자인 156)

- 요구(대기열 B): 무엇이 올라가는 중·다 됐는지·왜 못 올렸는지 파일별로 한눈에. "못 올린다" 안내가 알림처럼 안 보임
- 지금 문제: 고를 때 못 읽은 파일은 '2개는 올릴 수 없어요'만 나오고 어느 파일인지 모름, 200장 넘게 고르면 말없이 잘림, 올리다 실패하면 진행 글과 같은 초록 칸(role=status)에 나와 눈에 안 띔, 칸마다 상태 없음
- 방식
  - 사진 칸 왼쪽 아래 작은 표시: '올리는 중'·'올림'(초록)·'못 올림'(빨강). 표시 바탕은 면 색(밝은/어두운 둘 다 글자 대비), 버튼 이름에도 상태를 붙임('2번째 사진 대표, 올림')
  - 못 올린 안내는 빨간 글 칸(`sp-p__toast--error`) 하나(`#up-alert`, role=alert): 올리다 실패한 이유(로그인 끝남·5GB·연결)와 고를 때 뺀 파일 목록(파일 이름 · 이유: 지원하지 않는 형식/2GB 넘는 영상/열 수 없는 파일, 200장 넘음). 새로 고르거나 올리기를 누르면 비움
  - 진행 글(`#up-status`)은 진행만
- 영향: `src/pages/upload.astro`, `src/styles/parent.css`, `tools/design/upstatus.py`(보드 UploadSending 고침 + UploadRejected·UploadFailed 새로), e2e `tools/e2e/upstatus.py`
- 예상 결과: 올리는 동안 칸에 올림/올리는 중이 보이고, 실패하면 그 칸에 못 올림 + 빨간 안내, 고를 때 뺀 파일은 이름과 이유가 보임
- 결과: 리뷰 3회 반영(목록 10줄까지·200장 줄은 맨 앞이라 '외 N개'가 파일 수와 맞음, 올리는 동안은 칸 상태만 바꿈(새로 그리지 않음), 5GB가 차면 남은 칸 모두 못 올림, 다시 누르면 못 올림 지우고 이어서, 그룹을 고르면 그 안내만 지움, 실패 뒤 누른 버튼으로 포커스, 320px에서도 표시가 잘리지 않음(띄어쓰기에서 줄바꿈), '0장까지' 문구 없음). 검사 `tools/e2e/upstatus.py` 23개, retry(빨간 칸으로 바꿈)·shrink·bigvideo·upgrid 통과, astro check·build·단위 검사 통과

### 84. feature/view-bare — 크게 보기 한 번 누르면 사진만 (완료, dev 머지 0.4.29, 디자인 157)

- 요구(대기열 C): 크게 보기에서 화면을 한 번 누르면 위 메뉴·아래 판(반응·한마디)·화살표·영상 막대가 사라지고 사진만, 다시 누르면 돌아옴. 보드 PhotoView에 이미 있는 누르기 전환('메뉴 숨기기'/'메뉴 보이기', 숨기면 검은 바탕)을 따르고 숨긴 상태 보드 PhotoViewBare를 추가(157)
- 방식
  - `Viewer.astro` 스크립트: 사진 칸(`.sp-v__stage`)을 누르면 `.sp-v[data-bare]` 켜고 끔. CSS로 위 메뉴·화살표·재생 버튼·아래 묶음·토스트를 숨기고 바탕 검정. 넘겨 보기(스와이퍼)로 바뀌어도 그대로
  - 사진 칸 전체를 덮는 버튼은 손가락 넘기기를 막으므로 쓰지 않고, 키보드·화면 읽기용으로 포커스하면 보이는 '메뉴 숨기기/메뉴 보이기' 버튼(스크립트가 만듦)을 둔다. Esc로도 돌아옴
  - 영상: 재생 중엔 지금처럼 누르면 일시정지(이미 메뉴 숨김). 멈춘 상태에서 누르면 사진과 같이 전환
  - 스크립트 없으면 지금 그대로(가족 화면 0KB 원칙의 예외인 크게 보기 스크립트 안에서만)
  - 알고 둔 것: 넘기다 영상 칸에 멈추거나 영상 화면에서 옆으로 밀면 새 화면을 열어 메뉴가 다시 보임(영상은 페이지를 새로 여는 구조). 빠르게 두 번 누르면 두 번째는 버림(깜빡임 방지). 사진만 상태에선 화살표가 없어 PC는 한 번 눌러 메뉴를 켠 뒤 넘김. 화살표·수정 버튼 옆 빈 곳도 사진을 누른 것으로 봄
- 영향: `src/components/Viewer.astro`, `src/styles/family.css`, `tools/design/viewbare.py`, e2e `tools/e2e/viewbare.py`
- 예상 결과: 사진을 누르면 사진만, 다시 누르면 돌아옴. 넘겨도 사진만 상태 유지, 키보드로도 전환
- 결과: 리뷰 3회 반영(사진만 켜면 토스트 지움·사진만 중에 온 토스트는 읽기만(숨긴 토스트가 나중에 다시 뜨지 않게), 마우스로 끌다 놓기·빠른 두 번째 누름은 버림, 일시정지 버튼은 메뉴도 돌려줌, 투명도 줄이기·포커스 테두리). 검사 `tools/e2e/viewbare.py` 19개, vswipe·comments 통과(vplay는 원래 있던 "한마디 보냄 토스트"만 실패), 가족 `/album` 화면도 직접 확인, astro check·build·단위 검사 통과

### 85. feature/account-layer — 계정 탈퇴 확인 레이어·홈 화면에 두기 안내 그 자리에서 (완료, dev 머지 0.4.30, 디자인 이미 있음: Account·AccountDelete·AccountDeleteSub)

- 요구(다음 할 일 1-6): 페이지 이동 줄이기 마지막. 계정의 탈퇴 확인을 다른 화면 대신 이 화면 위 레이어로, 조부모 홈 화면에 두기 안내의 부탁하기·알겠어요·다음에를 이동 없이 그 자리에서
- 방식
  - 계정: 보드대로 묶음 줄(로그아웃·탈퇴하기), 이름 칸에 카카오 아이콘. 탈퇴하기는 `dialog.sp-layer__modal` showModal(사진 지우기 레이어와 같은 방식). 왼쪽 정렬·우는 얼굴(`public/sad.svg`)·두 버튼 같은 너비, 체크 전엔 탈퇴하기 흐리게(눌리면 브라우저 기본 안내). 구독 중이면 같은 자리에 '구독 중이에요' 레이어. 스크립트 없으면 `?confirm=`으로 같은 레이어를 연 채 다시 그림
  - 로그아웃은 보드에 확인이 없고 로그인 화면으로 가는 흐름이라 그대로(폼)
  - 홈 화면에 두기: `InstallGuide.astro` 스크립트가 폼을 `x-sp-inplace`로 보내고 `/install`은 204(다 됨)·409(부탁할 곳 없음). 판을 치우고 초점은 바로 아래 탭으로, 부탁하기면 숨겨 둔 알림을 보이고 초점. 스크립트 없으면 예전처럼 폼
  - 안내 판 배치(앨범 위 판)는 그대로, 보드의 아래 시트 모양은 이번 범위 아님
- 영향: `src/pages/settings/account.astro`, `src/components/InstallGuide.astro`, `src/pages/install.ts`, `src/styles/base.css`, `src/styles/parent.css`, `public/sad.svg`, e2e `tools/e2e/acclayer.py`(새), `install.py`·`delete.py`(이동 대신 레이어·판 사라짐 기다리기)
- 예상 결과: 탈퇴하기 → 주소 그대로 레이어(모달·Esc·바깥 누르기·취소로 닫힘, 체크해야 탈퇴), 설치 안내 버튼 → 이동 없이 판 사라짐
- 결과: 리뷰 3회 반영(로그아웃 줄 초점 테두리, 체크 전 탈퇴하기는 흐림 대신 바탕색+빨간 글자·테두리로 대비 4.5:1 이상(보드와 다름), 글자 200%면 두 버튼 위아래로, 닫으면 확인 체크 풀기, 설치 안내 401이면 다시 들어오기·서버 오류는 폼으로·모르는 값 400, 카카오 아이콘 색 토큰). 검사 `tools/e2e/acclayer.py` 29개, install·delete·photodel·homelayer 통과, astro check·build·단위 검사 통과
- 알고 둔 것: 스크립트 없이 연 레이어는 모달이 아님(사진 지우기와 같은 패턴, 뒤 화면에 inert 주기는 따로), 부탁할 곳이 없으면(409) 판이 그대로라 반응 없음(예전 폼과 같음), 구독 중 레이어의 '구독 관리' 버튼은 결제 화면이 없어 뺌, 카카오 아이콘은 mock 계정에 제공자가 없어 화면으로 못 봄

## 다음 이슈 (기획서 '개발 이슈 분할' 순서)

저장소는 `sweepea` 하나에 웹과 `supabase/`를 같이 둔다(혼자 개발, DB와 화면 변경을 한 PR에서 검증). iOS·안드로이드는 나중에 `sweepea-ios`, `sweepea-android`.

1. 확인(보류, 실기기 필요): 카톡 인앱 브라우저에서 출입증 쿠키 유지 (작은 테스트 페이지). 같이 확인: 카톡 → 외부 브라우저 자동 넘기기(`kakaotalk://web/openExternal`), `sms:` 문자 내용 미리 채우기(iOS·안드로이드), iOS 사파리 HEIC → JPEG 변환 시 촬영 시각 유지, iOS 26 사파리에서 공유 버튼 위치(홈 화면 추가 안내 문구 확정용)
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
13. supabase: 용량 집계, 5GB 상한. 정리 작업(예약, 출시 전 필수): 탈퇴 기한 지난 가족방 지우기(`sp_purge_deleted_families`) + `r2_cleanup` 폴더 R2 삭제, 하루 지난 `uploading` 사진과 그 R2 폴더, 완료된 사진 폴더에서 기록 안 된 파일(PUT마다 새 키라 남음) 지우기. 사진 지우기는 RPC로 용량 빼고 R2 삭제 대기열에
14. web: PC 화면 (모아 보기·크게 보기)

## 결정됨

- 이름: 스위피 / Sweepea (2026-10-23)
- 도메인: sweepea.co.kr 하나만. 다른 확장자 방어 등록은 하지 않음
- 앱 아이콘: 도트 콩이(3단계), 라이트 #E7F1F0 / 다크 #07221F 바탕 (2026-10-24)
- 키컬러: 틸 #0F766E / 다크 #2DD4BF, 떠 있는 버튼은 유리(주요는 색 유리, 보조는 투명 유리) (2026-10-24)
- 부모 로그인: 카카오 → 네이버 → Google → Apple. 시안엔 넷 다 두고, 구현 안 된 제공자는 버튼 비노출. Apple·Google은 공식 버튼·로고 규격 준수 (2026-10-24)
- 가족 화면 글자 크기: 기본값은 '기본'. 할머니·할아버지 호칭을 고르면 '크게'로 자동 선택(본인이 바꿀 수 있음). 모두에게 보이는 문구엔 '조부모' 대신 실제 호칭·'가족' 사용 (2026-10-24)
- 부모 소개 화면 3장(로그인 전 1회, 건너뛰기 가능). 조부모 쪽은 소개 없이 바로 사진 (2026-10-24)
- 부모 알림(승인·반응): 앱 출시 전까지 없음. 부모가 스위피를 열면 보임 (2026-10-24)
- 배우자: 별도 계정 초대 없이 가족처럼 링크 + 이름 + 비밀번호로 입장, 부모가 '올리기 가능' 권한만 추가. 모든 그룹 사진을 보고 올릴 수 있고 설정·승인은 못 함. 올리기 권한은 승인된 기기에만, 새 기기는 다시 승인 (2026-10-24)
- 탈퇴: 가족 화면은 바로 닫히고, 3일 유예 뒤 사진·가족·아이 정보 모두 삭제. 유예 중 다시 로그인하면 되살리기 가능. 이용약관·개인정보 처리방침은 출시 전 별도 작성 (2026-10-24)
- 올리기 권한 가족(배우자 등) 올리기 화면: 부모와 동일 (2026-10-24)
- 가족 화면 '홈 화면에 두기' 버튼: 투명 유리 대신 채운 버튼(fill) (2026-10-24)
- 높이 기준: 부모 입력·버튼·라디오 52, 칩·작은 탭 40, 목록 줄 56 / 가족 화면 입력·버튼·탭 56, 반응 버튼 60(이모지만, 2026-10-26 80에서 줄임) / 뒤로·탭바 44 (2026-10-24)
- 결제: 인앱결제(App Store·Google Play)만. 웹 결제는 보류. 해지는 스토어 구독 설정으로 안내 (2026-10-24)
- 구독 해지 뒤 원본: 남은 기간까지 그대로, 그 뒤 14일 동안 원본 내려받기 가능, 지나면 보기 좋은 크기(2048)로 줄임. 사진은 삭제하지 않음 (2026-10-24)
- 호칭: 사진 올린 사람은 실제 호칭(처음 설정의 엄마/아빠 선택 유지, '오늘 아빠가 올렸어요'), 부모 둘 다 해당하는 말(확인·승인·부탁·앨범 닫힘)은 '엄마아빠' (2026-10-25)
- 여러 가족방: 기기 하나가 여러 가족방에 들어갈 수 있게 DB부터 바꾼다(가족방마다 열쇠를 따로 만드는 방식 대신). 앨범은 모두 섞어 보기가 기본, 한 집만 골라 보기 가능 (2026-10-25)
- 사진 저장소: Cloudflare R2(보는 전송비 무료). DB는 Supabase. 올리기는 Worker 경유 (2026-10-25)
- 사진 반응: 앨범 칸에 하트·한마디 배지, 새 반응은 하트가 떠오르는 효과(한 번만, 동작 줄이기 시 끔) (2026-10-24)
- 화면 작업 순서: 디자인 파일(캔버스)을 먼저 고친 뒤 코드에 적용 (2026-10-26)
- 이동 표시: 왼쪽 위 뒤로가기는 글자만(‹ 없음), 오른쪽 이동은 꺾쇠 아이콘만(“확인 ›” 같은 글자 없음), 가족 크게 보기 "닫기"·"저장"도 글자만 (2026-10-26)
- 부모 아래 탭: 앨범 · 알림 · 설정, 알림에 새 반응 수 배지. 최근 반응은 알림 탭 (2026-10-26)
- 비밀번호 칸: 모두 가운데 정렬 (2026-10-26)
- 가족 크게 보기: 화면 가득 + 반투명 위 메뉴·아래 판(흰 75%/검정 65%), 이 화면만 작은 스크립트 허용. 영상은 재생하면 막대 줄만 남고 화면 누르면 일시정지, 자동 숨김 없음. 옆으로 밀기 + ‹ › 버튼 (2026-10-26)
- 반응 버튼: 이모지만(글자 없음). 넘겨 보기는 '직접 쓰기' 대신 카드마다 한마디 칸 (2026-10-26)
- 가운데 레이어: 들어오기 신청(부모)·승인 완료·새 사진(가족), 백일·돌·생일·저장 공간 90%(부모). 같은 일은 한 번, 저절로 안 사라짐. 구독 끝남 안내는 결제 이슈에서 (2026-10-26)
- 계정 이름: 부모 이름은 받지 않고 호칭('하린 엄마')으로 보임 (2026-10-26)
- 바로 저장되는 켜고 끄기(가족도 사진 저장하기·사진 올리기 허용): 토글. 설정 탭에 승인 대기 수 배지 (2026-10-26)
- 폰·PC 디자인: 같은 컴포넌트, 배치만 다르게. 아이 고르기는 한 줄 좌우 스크롤 세그먼트 탭 (2026-10-26, 34에서 적용)

## 확인 필요 (멈추지 않고 기록만, 2026-10-26~)

- main 머지 PR #1(dev → main) 열어 둠. 제목은 0.2.0 시절 그대로, dev는 0.4.14. 머지는 사용자 확인 뒤

- 운영 Supabase·R2에 적용해 쓰는 중(2026-10-26~). 마이그레이션은 이제 새 파일로만
- 네이버 로그인은 Supabase 기본 제공자가 아니라 제공자 이름이 '로그인'으로 보일 수 있음
- 홈 화면에 두기 실기기: 아이폰 사파리 공유 버튼 위치(iOS 26은 ⋯ 안), 홈 화면 앱이 사파리 출입증 쿠키를 이어받는지, 안드로이드 크롬 '앱 설치' 문구. 삼성 인터넷·아이폰 크롬 등은 아직 안내 안 함
- Cloudflare Workers 요금제(무료면 요청당 외부 호출 50개): 정리 작업은 45개 안에서 멈추고 다음 날 이어서 함. 큰 가족방 탈퇴는 며칠 걸릴 수 있음. 유료면 한도 올리기
- 올리기 화면을 하루 넘게 열어 두었다 다시 누르면(정리 작업이 지운 사진) 끝난 것으로 보일 수 있음
- 카톡 인앱 브라우저 → 외부 브라우저 넘기기와 출입증 이어 주기(넘어가면 쿠키가 없어 다시 이름·비밀번호). 실기기 확인 뒤 방식 결정
- 아이폰 사진 저장(사진 앱 대신 '파일')·카톡 인앱 브라우저 `download` 무시 여부(실기기)
- 가족 플랜 줄은 아직 화면에 없음(결제 이슈에서)
- 설정 하위 화면 제목: 디자인은 뒤로 줄 가운데 작은 제목, 코드는 아래 큰 제목. 맞출지(35에서 발견)
- 접종·검진 일정 데이터: 질병관리청 원문(nip.kdca.go.kr)을 자동으로 못 읽어 보건소 게시본으로 맞춤. 출시 전 원문과 대조. 구강검진 시기는 보건소마다 표기가 달라(4·6·7차 vs 18~29·30~41·42~53·54~65개월) 아직 안 넣음. A형간염 2차 간격(제품마다 6~12/18개월)·폴리오 3차(6개월 vs 6~18개월)도 원문 대조

## 결정 필요

- 국가 권장(유료·선택) 예방접종 추가(사용자 2026-10-26): 질병관리청 공개 API에 일정 데이터는 없어 보임(국가건강정보포털 API는 건강 정보 글, 공공누리 4유형). 지금처럼 질병관리청 표준 예방접종 일정표를 원문 대조해 앱에 넣는 방식 → 인플루엔자(매년)·HPV·로타 등 어디까지 넣을지, '국가 필수'와 '선택'을 나눠 보여 줄지


- 화면 문구 규칙(브랜드 리뷰 2026-10-24 반영): 실제 가족 호칭 사용, "카톡" 통일, 날짜 "~부터", 접종 일정은 출시 전 질병관리청 표준 일정과 대조

- Pretendard 글꼴: 동적 서브셋(CDN) vs 직접 서브셋 생성 — 첫 화면 성능 측정 후 결정
- 최소 지원 브라우저 (카톡 인앱 브라우저 기준)

### 86. feature/vt-abort — 페이지 전환 취소 오류 막기 (완료, dev 머지 0.4.31)
- 사용자 보고(2026-10-28): 크롬 콘솔에 `Uncaught (in promise) InvalidStateError: Transition was aborted because of invalid state. ViewTransition opt-in disabled`가 자꾸 찍힘(home)
- 원인: 다른 문서로 넘어가는 전환(`@view-transition`)을 브라우저가 건너뛰면(전환 중 화면이 가려지는 등) pageswap/pagereveal의 `viewTransition.ready`가 거부되는데 받는 곳이 없음. 이동은 정상
- 고침: `src/layouts/Base.astro` head에 인라인 스크립트, 두 이벤트의 ready·finished·updateCallbackDone을 받아 둠
- 검증: skipTransition을 강제로 넣어 고치기 전 이동마다 `Transition was skipped` 오류 → 고친 뒤 0, 보통 이동은 전환 그대로. acclayer e2e 통과, QA 1회(지적 2개 반영: 주석을 JS 안으로, `p?.catch`)
- 못 한 것: 실제 '화면 가려짐' 상황은 헤드리스에서 재현 못 함, 사파리 실기기

### 87. feature/taken-at — 찍은 날짜 제대로 읽기 (완료, dev 머지 0.4.32)
- 요구: 지금은 JPEG만 EXIF 촬영 시각을 읽고 HEIC·PNG·영상은 파일 시각(`lastModified`)을 써서, 아이폰은 고른 시각·내보낸 시각이 들어가 앨범 달이 틀어질 수 있음
- 구현
  - 사진: 종류 표시(`file.type`) 대신 파일 앞부분 바이트로 판별. JPEG(지금대로), HEIC/HEIF(meta 상자의 iinf·iloc에서 Exif 항목 위치를 찾아 그 부분만 읽음), PNG(eXIf 덩어리). 같은 TIFF 읽기(`readTiff`)를 씀
  - 영상: mediabunny `getMetadataTags().date`(아이폰 `com.apple.quicktime.creationdate`, 시간대 있음) → 없으면 MP4/MOV `moov/mvhd` 생성 시각(UTC, 1904 기준) → 없으면 파일 시각. 범위(아래 plausible) 밖은 버림. mediabunny date는 ©day·rldt·date·creationdate 중 먼저 읽힌 값이라 날짜만 있는 ©day가 먼저면(자정 UTC) mvhd로 넘어감
  - 출처 값은 DB에 있는 값만 되므로 파일 안 시각은 'exif', 파일 시각은 'file'
- 영향 파일: `src/lib/exif.ts`, `src/pages/upload.astro`(photo·video), `tests/exif.test.ts`, `tools/e2e/takenat.py`, (함께 고침) `src/lib/parent.ts` `seoulDate`, `src/pages/view/[id].astro`·`album/[id].astro`·`album/save.astro`, `tools/e2e/save.py`
- 예상 결과: 아이폰 HEIC·영상, 안드로이드 영상이 찍은 날짜로 앨범에 묶임
- 믿을 만한 범위(`plausible`): 2001년~지금+10분. 밖이면 파일 시각(1980년 초기화 카메라, 현지 시각을 UTC로 적은 영상이 미래가 되는 경우, 정보 수정 화면 범위 2000~오늘 밖이면 저장이 막히므로)
- 하지 않는 것: WebP(EXIF가 보통 파일 끝이라 앞부분만 읽어서는 못 찾음), PNG 스크린샷의 XMP 날짜
- 알려진 한계: 홈은 찍은 날 최신 200장만(album.ts shortcut). 사진 200장 넘는 가족이 옛날 사진을 올리면 올린 직후 홈에 안 보일 수 있음 → 다음 할 일 3(더 불러오기)에서 해결
- 함께 고침: 저장 파일 이름 날짜가 UTC 날짜(`taken_at.slice(0,10)`)라 한국 아침 사진이 전날로 붙던 것 → `seoulDate`(view·album/[id]·album/save)

### 86b. fix/vt-uncaught — 전환 오류가 사진 화면에서 계속 찍힘 (완료, dev 머지 0.4.33)
- 사용자 보고(2026-10-28): 86 뒤에도 사진 크게 보기 주소에서 같은 오류. 헤드리스에선 일반 화면으로 재현 못 함(화면이 가려진 채 열릴 때 크롬이 페이지에 건네지 않은 전환을 취소하는 것으로 추정, 확실하지 않음)
- 재현된 것: 앱에서 없는 주소로 가면 기본 404 화면(앱 바탕 아님)에서 같은 오류
- 고침: Base에 `unhandledrejection`에서 'Transition …' DOMException만 막기(다른 오류는 그대로), `src/pages/404.astro`(Base + 안내)
- 검증: 전환 오류 거부는 안 찍히고 다른 오류는 찍힘, 앱→없는 주소 오류 없음, 404 상태 코드·제목

### 88. feature/load-more — 아래로 내리면 60장씩 끝까지 더 불러오기 (완료, dev 머지 0.4.34)
- 요구(사용자 2026-10-28 확정): 사진이 많을 때 아래로 내리면 자동으로 60장씩 더, 상한 없음. 지금은 최근 200장까지만(홈·가족 앨범·크게 보기)
- 디자인 먼저(캔버스에 없음): 목록 끝 줄 세 상태 보드 — 불러오는 중(콩이 작게 + '사진 불러오는 중…'), 스크립트 없을 때 '사진 더 보기' 버튼, 끝('처음 사진까지 모두 봤어요'). 부모 홈·가족 모아 보기 두 화면, 라이트·다크
- 구현
  - 백엔드: `listMedia`에 `before`/`after` 커서((taken_at, id), 찍은 날 내림차순 기준 더 옛날/더 최근)와 `id` 추가, `countMedia`(같은 조건 개수, PostgREST `Prefer: count=exact`) 추가. supabase·mock 둘 다
  - 부모 홈: 처음 60장. 끝에 '사진 더 보기' 링크(`?before=<커서>`, 스크립트 없으면 그 쪽만 그린 페이지). 스크립트 있으면 끝 줄이 보이기 전(IntersectionObserver, 여유 600px) 다음 쪽 HTML을 받아 붙임. 같은 달이 이어지면 그 달에 칸을 합치고 엇갈린 배열(masonry)을 다시 계산, 달 사진 수도 갱신
  - 가족 앨범: 모아 보기는 날짜 묶음을 같은 방식으로 이어 붙임(같은 날이면 합침). 넘겨 보기는 남은 폭이 화면 6개쯤일 때 다음 쪽 카드를 붙임. 제목 'N장'·'n / 전체'는 countMedia로 정확히
  - 크게 보기(부모 view·가족 album/[id]): 200장 목록 대신 그 사진 앞뒤 21장(커서)과 개수로 자리·전체를 구함 → 몇 번째 사진이든 열림
  - 붙이는 동안 화면 읽기: 늘 있는 빈 알림 칸(role=status) 하나에 '불러오는 중'·'N장을 더 불러왔어요'·'모두 봤어요'를 바꿔 씀. 키보드로 '사진 더 보기'에 와 있었으면 붙인 첫 칸으로 초점
  - 닫으면 보던 자리로(사용자 2026-10-28 "닫기 누르면 현재 보던 상태로 돌아가는 게 중요"): 크게 보기 닫기 주소에 지금 보는 사진을 담아(`?to=<id>#c-<id>`, 넘기면 주소도 바뀜) 목록이 그 사진까지(그 쪽 끝까지) 그리고, 누를 때 칸의 화면 속 높이를 sessionStorage에 적어 두었다가 돌아오면 같은 높이에 오게 스크롤. 넘겨 보기는 그 카드가 가운데(`#p-<id>`, 지금도 쓰는 방식). 스크립트 없으면 #앵커로 그 칸이 맨 위
- 영향 파일: `src/lib/backend/{types,supabase,mock}.ts`, `src/lib/album.ts`, `src/lib/more.ts`(새), `src/pages/home.astro`, `src/pages/album/{index,[id],save}.astro`, `src/pages/view/[id].astro`, `src/styles/base.css`, `tools/design/loadmore.py`(캔버스 v159~160), `tools/e2e/loadmore.py`
- 하지 않는 것: 골라서 저장하기 화면(`/album/save`)은 최근 200장 그대로(여러 장 골라 저장은 최근 사진 위주, 필요하면 같은 방식으로)
- 예상 결과: 사진 몇 장이든 끝까지 내려 볼 수 있고, 홈에서 연 옛날 사진도 크게 보기에서 앞뒤로 넘어감
- 정한 것(구현하며): ?before=에 기준 사진 id 대신 커서 값(찍은 날~id, ISO 꼴만)을 실음(그사이 지워져도 이어짐), 순번은 전체-커서보다 옛것. 닫고 돌아올 때 한 번에 900장까지(Supabase max_rows 1000 아래), 넘으면 그 위 30장부터 한 쪽(위로 이어 붙이기 없음, shortcut). 홈 달 사진 수는 쪽 경계에 걸칠 수 있는 첫·끝 달만 따로 셈. 새 사진 레이어는 계속 최근 200장 기준. 반응 수는 DB 함수가 200장씩이라 나눠 물음(mock도 같은 상한). 가족 앨범 화면에 작은 스크립트 예외 추가(없으면 링크·#앵커)
- 결과: 검토 3회(1회: 넘겨 보기 반응 뒤 첫 카드로 튐·900장 넘는 자리·지워진 기준 사진·화면 읽기 알림·초점·버튼 대비, 2회: 스크립트 없는 다음 쪽 제목 0장·커서 엄격 확인·순번·올라온 날, 3회: 201번째부터 반응 수 빠짐·카드 id 겹침·낡은 주석), 모두 고침. loadmore e2e 25개(130장, 달·날 걸침, 끝 줄, 닫으면 같은 높이, 넘겨 보기 반응 뒤 그 카드, 스크립트 없음), QA 커서 시험(같은 시각 여럿·지워진 기준·MAX_ROWS 1000), 운영 Supabase에 새 조회 문법 확인(anon, 0행), 기존 e2e(save·family·delete·homelayer·masonry·comments·instant·chev·kidtabs·vplay 새 부분) 통과
- 못 한 것: 실제 사진 많은 가족 데이터·실기기(아이폰 사파리 돌아온 높이·VoiceOver 알림)·900장 넘는 자리 화면 확인. vplay '한마디 보냄 토스트'는 원래부터 실패(이번 변경과 무관)

### 89. feature/family-masonry — 가족 모아 보기 2줄을 엇갈린 배열로 (완료, dev 머지 0.4.35)
- 요구(사용자 2026-10-28 "그게 나을까?" → 추천대로): 가족 모아 보기 기본 크기(2줄, 넓은 화면 4줄)는 CSS columns라 같은 날이 쪽을 넘어 이어져 칸을 합치면 그날 사진이 줄 사이로 다시 나뉘어 보이던 칸이 옆 줄로 옮겨감(리플로우). 순서도 줄마다 위→아래로 읽힘
- 구현: 부모 홈과 같은 엇갈린 배열(`src/lib/masonry.ts`, 가장 짧은 줄에 차례로 쌓기, 디자인 GrandList 보드도 같은 방식). 서버가 날짜 묶음마다 2줄·4줄 자리를 `--c2/--r2/--s2`·`--c4/--r4/--s4`로 내보내고, 이어 붙여 합치면 브라우저가 그 묶음만 다시 계산(앞 칸 자리는 그대로). 다시 계산하는 함수는 `src/lib/more.ts`로 옮겨 홈과 같이 씀. 1줄(columns 1)·3·5줄(정사각형 격자)은 그대로
- 영향 파일: `src/pages/album/index.astro`, `src/styles/family.css`, `src/styles/parent.css`, `src/lib/more.ts`, `src/lib/masonry.ts`(주석), `src/pages/home.astro`, `tools/e2e/loadmore.py`
- 예상 결과: 사진이 늦게 오거나 다음 쪽을 합쳐도 보이던 칸이 움직이지 않음
- 범위 바뀜(검토 2회): 칸 폭 단위(cqi)·container query가 없는 옛 브라우저(iOS 15 이하) 대비 `@supports not (container-type: inline-size)` — 가족 2줄은 CSS columns, 부모 홈(이미 배포된 엇갈린 배열)은 정사각 격자
- 결과: 검토 3회(1회: 주석·e2e 비율 섞기, 2회: 옛 브라우저 대비, 3회: 쓸모없는 대비 줄·주석·문서), loadmore e2e 28개(쪽 경계에 걸친 날을 합쳐도 움직인 칸 0, 겹침 0, 휴대폰 2줄, 비율 섞음), QA로 세 쪽에 걸친 날 두 번 합치기·폭 바꾸기·z 전환·스크립트 없는 다음 쪽 확인, 대비 규칙은 CSS를 넣어 390·1280폭 겹침 0
- 못 한 것: 실제 iOS 15 이하 사파리, 사진 많은 실제 가족 데이터. 아주 긴 파노라마는 칸에 맞게 잘림(부모 홈·디자인과 같은 규칙, 크게 보기에선 전체)

### 90. 도메인 연결 sweepea.co.kr + www (완료, dev 머지 0.4.37)
- 요구(사용자 2026-10-28): 도메인 연결, "www도 같이 연결되어야 해"
- 지금(2026-10-28 확인): 네임서버가 아직 가비아(ns.gabia.co.kr 등). 로컬 wrangler 로그인 안 됨(배포는 dev 푸시로 자동)
- 사용자 할 일: ① Cloudflare `Takeaseat.cs@gmail.com's Account`에 사이트 `sweepea.co.kr`(Free) 추가 ② 가비아에서 네임서버를 Cloudflare가 준 2개로 ③ Active 될 때까지 대기 ④ 연결 뒤 Supabase > Authentication > URL Configuration에 `https://sweepea.co.kr/auth/callback`(Site URL도 새 주소) 추가
- 진행: 사용자가 Cloudflare 사이트 추가(Free, AI 학습 크롤러 막기 추천)·가비아 네임서버 ed/jade.ns.cloudflare.com(3차 ns.gabia.net 지움)·Active(2026-10-28). 코드: wrangler.jsonc routes·vars·keep_vars, 미들웨어 www → 308. 0.4.36에서 routes 때문에 workers.dev가 꺼짐(1042, 실수) → 0.4.37 `workers_dev: true`
- Supabase(2026-10-28): 처음엔 새 주소가 허용 목록에 없어 카카오 로그인 뒤 Site URL(workers.dev 첫 화면)로 떨어짐(인증 기록으로 확인) → 사용자가 Site URL `https://sweepea.co.kr`·Redirect URLs에 `/auth/callback` 추가, 로그인 뒤 /home 확인
- 할 일(Active 뒤): `wrangler.jsonc`에 `routes`로 `sweepea.co.kr`·`www.sweepea.co.kr` custom_domain, `www`는 `src/middleware`에서 같은 경로로 `sweepea.co.kr`에 301(주소 하나로: 가족 링크·로그인 쿠키가 주소에 묶임), `SITE_ORIGIN=https://sweepea.co.kr`(공유 링크), 배포 뒤 두 주소·로그인·공유 링크 확인. workers.dev 주소와 이미 보낸 링크는 계속 열림

### 91. feature/landing — 대표 첫 화면에 소개 노출(검색 등록용) (완료, dev 머지 0.4.38)
- 요구(사용자 2026-10-28): 처음 온 사람이 sweepea.co.kr에 들어오면 "가족에게 받은 주소로 들어와 주세요"만 나와 엄마아빠는 막힘. "메인 진입 시 뭔가 있어야 서치 콘솔에도 등록" → "일단 루트에 컨텐츠 노출되는 걸로"
- 디자인: 캔버스 Landing·Landing-Light(v161~, `tools/design/landing.py`). 위 콩이·스위피·한 줄 소개(로그인 보드와 같음) + '시작하기' + 가족 안내 한 줄, 가운데 소개 3장 그림·제목(h2, title-2)·설명, 아래 '시작하기'·바닥글
- 구현: `/`에 처음 온 사람(부모 쿠키·가족 출입증 없음)은 소개 화면. 이미 들어온 기기는 지금처럼 앨범·대기로. 로그인 화면(`sp-p__brand`·`sp-p__login`)·소개 화면(`sp-p__mock*`·`sp-p__intro-*`) 스타일 재사용. 검색용: 제목·설명, 공유 미리보기(og:title·description·image), 대표 주소 canonical, `public/robots.txt`(/api/만 막음, 나머지 화면은 미들웨어 X-Robots-Tag noindex — 아래 '바뀜'), `public/sitemap.xml`
- 영향 파일: `src/pages/index.astro`, `src/layouts/{Base,Parent}.astro`, `src/middleware.ts`, `src/styles/parent.css`, `public/robots.txt`, `public/sitemap.xml`
- 바뀜(검토 1회): robots.txt로 첫 화면 말고 다 막으면 카톡 스크랩 봇이 가족 링크(/i/) 미리보기를 못 만들 수 있음 → robots.txt는 /api/만 막고, 첫 화면 밖 모든 응답에 `X-Robots-Tag: noindex, nofollow`(미들웨어). 글자 200%에서 소개 그림 카드가 화면을 넘던 것(/start도) → 감싼 칸 max-width·이름 줄어들기
- 하지 않는 것: 개인정보처리방침·이용약관(따로), 서치 콘솔 소유 확인(사용자가 DNS TXT 또는 확인 코드)
- 결과: 검토 3회(1회: robots→noindex 머리·200% 넘침, 2·3회: 소개 카드 칩 줄바꿈·문서), 로컬 Lighthouse LCP 약 1.4초·CLS 0·접근성 100·JS 0, 기존 e2e(entry·parent) 통과
- 남은 확인: 운영에서 카카오 공유 디버거로 /i/ 미리보기(사용자 로그인 필요), 운영 robots.txt에 Cloudflare 봇 설정이 덧붙는지. 디자인과 다른 점: 소개 그림 카드는 /start 구현을 그대로 써서 보드보다 글자가 작고 셋째 카드의 콩이가 카드 안(보드는 위)

### 정한 것: 게스트(로그인 없이 혼자 쓰기) 없음 (사용자 2026-10-28)
- 사용자 "게스트 서비스 막아야겠는데": 로그인 없는 계정(익명 로그인)·기기에만 저장하는 방식 모두 만들지 않는다
- 이유(논의): 기기를 잃으면 사진에 다시 들어올 수 없고, 누구나 저장 공간을 쓸 수 있어 한도·정리 규칙이 필요하며, 기기 저장은 사파리가 7일 뒤 지울 수 있어 '사라지지 않는 앨범'과 맞지 않음
- 지금 상태가 곧 막힘: 올리기는 부모 로그인(카카오 등)만, 가족은 부모 링크 + 승인으로만. 첫 화면 '시작하기'도 로그인으로 감

### 92. feature/landing-copy — 첫 화면 문구를 마케팅 관점으로(카피라이팅 스킬 + 리서치) (완료, dev 머지 0.4.39)
- 요구(사용자 2026-10-28): "루트 진입 컨텐츠 마케팅 스킬 + 리서치 통해서 업데이트"
- 리서치(2026-10-28 웹 검색): 경쟁 앱(패밀리 앨범·BabyAlbum·Bebememo)은 모두 앱 설치. 패밀리 앨범은 공개 범위 세분화가 유료(프리미엄). 카톡으로 보낸 사진은 서버 보관 기간이 지나면 만료되고(블로그는 약 30일, 공식 확인 못 함 → 숫자 안 씀) 화질 설정에 따라 줄어듦. 키워드 검색량 수치는 못 얻음(네이버 검색광고 키워드 도구 필요)
- 구조(사람이 움직이는 세 박자: 지금 불편 → 바뀐 모습 → 시작 방법): 머리(제목에 검색어 '아기 사진'·'가족 앨범'·'조부모') → 이런 적 있으세요?(불편 3) → 이렇게 써요(3단계) → 좋은 점 3(지금 소개 그림 재사용) → 자주 묻는 질문(details/summary, FAQPage 구조화 데이터) → 마지막 시작하기
- 사실만: 조부모 앱 설치·가입 없음(처음 한 번 이름·가족 비밀번호), 처음 들어오는 사람은 승인, 외가·친가 그룹, 무료 5GB(차면 새로 올리기만 멈춤), 보기 좋은 크기로 줄여 올림(영상 1080p, 원본 보관 안 함), 지우기 전까지 보관. 지어낸 숫자·후기 없음
- 영향 파일: `src/pages/index.astro`, `src/styles/parent.css`, `tools/design/landing.py`(캔버스)
- 바뀜(사용자 2026-10-28): "한 장으로 설명되면 좋겠는데" → 불편·단계·그림 카드·질문(FAQ 구조화 데이터 포함) 빼고 휴대폰 한 화면(제목·한 줄·핵심 3줄·무료로 시작하기·가족 안내). "후킹이 저 정도로밖에" + "서비스 모르는 사람 기준" → 처음 보는 사람이 내 얘기로 느끼는 제목 A(단톡방) 선택, "말투.." → '아직도'(나무람) 빼고 "아기 사진, 단톡방에 올리고 계신가요?"
- 최종(사용자 피드백 차례로): "설명 문구가 너무 구리다" → 말 대신 장면, "카톡 대화 말고 서비스 화면" → 할머니가 링크로 보는 넘겨 보기를 휴대폰 그림에(양옆 이전·다음, 반응 5가지, 한마디, 사진 칸에 콩이 — 그린 부분만 자른 `public/kongi-crop.svg`), "디바이스 하단 그라디언트로 잘라" → 실제에 가까운 크기 + 아래 테두리만 흐림, "테두리 밝아지면 핸드폰 아님" → 몸체는 검정 그대로 + 얇은 금속선 + 다크에서 민트 빛. 화면: 콩이·스위피 / "아기 사진, 단톡방에 올리고 계신가요?" / "링크 하나만 보내세요. 할머니는 앱 설치도 가입도 없이 봐요." / 휴대폰 그림(aria-hidden) / 외가·친가 따로·하트·한마디·지우기 전엔 그대로 / 무료로 시작하기·5GB까지 무료·가족 안내. 390×844 한 화면(실제 사파리는 주소창 때문에 아래가 조금 걸릴 수 있음)
- 검토: 4회(긴 판 사실 확인, 한 장 판 사실·말투, 서비스 화면 판: 태그 선택자 b → 클래스, '누르기만 하면'은 처음 이름·비밀번호를 넣으니 사실 문구로, 없는 색 --ph-2(보드 전용) → --fill, 그림자 잘림 → 덱 가로만 clip, 이모지 글꼴, 큰 글자에서 칩 겹침), Lighthouse 통과
- 검토 1회(긴 판 기준)에서 나온 사실 확인: 설치·가입 없음은 조부모 얘기로, 승인은 '처음 보는 이름은 확인'(등록된 이름의 새 기기는 비밀번호만), 영상 1080p는 줄일 수 있을 때만(한 장 판에선 뺌). /start 3장 "콩이도 아이 나이에 맞춰 자라요"는 코드에 없음(콩이 그림 한 장) → 사용자에게 물음

### 93. iOS 앱(전체 네이티브) 계획 (계획 검토 중)
- 결정(사용자 2026-10-28): 조부모도 웹과 앱 둘 다로 본다 → 앱 하나에 입구 둘(엄마아빠 로그인 / 가족 링크). 화면은 **전부 네이티브(SwiftUI)**, 디자인 캔버스 그대로. 기획서의 "조부모는 앱 없음"·"웹을 감싸는 앱"은 이 결정으로 바뀜
- 저장소: `sweepea-ios`(새로, xcodegen 프로젝트, SwiftUI, Supabase Swift SDK). 백엔드는 지금 Supabase·Worker 그대로 같이 씀
- 웹(이 저장소)에 더할 앱용 입구: ① API가 쿠키 말고 `Authorization: Bearer` 토큰도 받기(올리기·공유·설치 등) ② 사진 주소 서명 API(볼 권한 확인 후 `/m/…` 서명 주소 묶음 발급, 서명 비밀은 서버에만) ③ 유니버설 링크용 `/.well-known/apple-app-site-association`(가족 링크 `/i/*`를 앱이 열게, 애플 Team ID 필요) ④ Supabase 로그인 돌아올 주소에 앱 주소(`sweepea://auth/callback`) 추가(사용자)
- 단계
  1. 바탕: 프로젝트 골격, 디자인 값(색 밝음·어두움, 글자 단계·가족 큰 글자 3단계, 간격·모서리 — tokens.css와 같은 값), Pretendard 글꼴(OFL), 콩이, 공통 부품(채운 버튼·카카오 버튼·회색 알약·칩·토스트·가운데 레이어·세그먼트 탭·아래 탭바)
  2. 입구: 첫 화면(웹 첫 화면과 같은 소개), 엄마아빠 로그인(카카오, ASWebAuthenticationSession + PKCE), 처음 설정(아이·가족 비밀번호), 가족 링크 입장(누구세요 → 비밀번호 → 승인 대기·앨범), 유니버설 링크
  3. 가족 화면: 앨범 넘겨 보기·모아 보기(엇갈린 배열, 60장씩 더), 크게 보기(반응·한마디·저장), 안내 화면들
  4. 엄마아빠 핵심: 홈(달별 엇갈린 배열·레이어), 크게 보기·사진 정보 수정·지우기, 올리기(사진첩에서 고르기, 기기에서 줄이기 — 영상 AVFoundation, 백그라운드 이어 올리기), 카톡 공유(카카오 SDK)·공유 창, 최근 반응
  5. 설정: 가족(승인·거절·새 휴대폰·링크·문자), 그룹, 아이·접종 일정, 글자 크기, 저장 용량, 계정(탈퇴·되살리기)
  6. 앱에서만: 푸시(새 하트·한마디·승인 요청), 업로드 추천(사진첩 얼굴 감지), 앱 안 결제(나중)
- 사용자에게 필요한 것: 애플 개발자 계정·Team ID, 번들 ID(제안 `kr.co.sweepea.app`), 최소 iOS 버전(제안 17), 카카오 개발자 콘솔 iOS 앱 등록(네이티브 앱 키), GitHub `sweepea-ios` 저장소 만들기(비공개 추천) 동의
- 진행 방식: 단계마다 웹과 같은 규칙(디자인 캔버스 먼저, 기능마다 검토·검증 3회, dev 브랜치)

### 94. 경쟁력 기능과 요금제 (정함·계획, 2026-10-29)
- 배경(사용자 "경쟁력을 만들어야 하는데"): 국내 강자(쑥쑥찰칵·Bebememo, 평가 1.6만~1.8만)와 같은 값(월 ₩5,900 안팎)이면 엄마아빠가 고를 이유가 '조부모 설치 없이' 하나로는 약함. 돈 내는 사람은 엄마아빠라, 엄마아빠가 "다른 앱엔 없다"고 느낄 것을 만든다(research/pricing-2026-10.md)
- 경쟁력 기능(조부모가 앱 없이 우리 웹으로 보는 구조라서 자연스럽게 되는 것)
  1. **할머니가 보신 걸 엄마아빠에게**: 이번 주 누가 몇 번 봤는지, 어떤 사진을 여러 번 봤는지(조부모 화면이 우리 웹이라 셀 수 있음, 앱을 깔아야 하는 경쟁사는 조부모가 안 깔면 못 셈)
  2. **조부모 음성 한마디**: 글자 대신 말로 남기고 엄마아빠는 목소리로 들음(웹 녹음). 손주가 커서도 남는 할머니 목소리. **받아 적은 글자도 같이 보임**(사용자 "텍스트로 보이긴 해야": 소리를 못 켜는 곳에서도 읽게). 말하면 자동으로 글자로 바뀌고, 보내기 전에 글자를 보여 줘 고치거나 다시 말하게. 엄마아빠 화면엔 글자 + 재생 버튼. 받아 적기 방법은 만들 때 정함: 브라우저 음성 인식(무료, 카톡 안 브라우저 지원 확인 필요) 또는 서버 음성 인식(정확, 건당 비용)
  3. **액자 모드**(우선순위 뒤, 사용자 "있어서 나쁠 건 없어 보여서 추가"): 태블릿·TV 브라우저에 열어 두면 새 사진이 저절로 넘어가는 화면. 태블릿이 있는 댁만 쓰므로 핵심은 아님
- 요금제(안, 아직 하나/둘 미정): 무료 = 핵심 경험 전부(설치 없이 보기·외가/친가·승인·하트·한마디·광고 없음) + 줄인 사본 5GB / '스위피 플러스' 월 ₩5,900·연 ₩59,000 = 원본 보관(사진·영상 원본, 아직 없는 기능) 100GB + 음성 한마디 계속 보관(무료는 최근 것만) + 액자 모드. 꽉 채워도 저장 비용으로 적자 없음(월 54%·연 45%, 서버·DB 비용 빠짐). 가족 플랜(월 ₩11,900·200GB)은 차별점이 생기면 추가
- 순서(제안): 1 보신 기록 → 2 음성 한마디 → 원본 보관 → 3 액자 모드. 웹에 먼저 만들고 iOS 앱에 같은 것. 각각 디자인 캔버스 보드 먼저
- **정함(사용자 2026-10-29)**: 스위피는 보관(클라우드)이 아니라 가족에게 보여 주는 곳(사용자 "생각해보면 클라우드가 아닌데") → **원본 보관은 안 만든다**(아이클라우드 200GB ₩4,400·2TB ₩14,000과 용량 싸움이 됨). **가족 플랜 없음**(₩11,900·200GB는 아이클라우드 2TB와 비교되면 짐). 요금제는 무료 + '스위피 플러스'(월 ₩5,900·연 ₩59,000) 하나: 가족이 보는 사본 용량 넉넉히(예: 100GB, 숨은 상한) + 음성 한마디 계속 보관 + 액자 모드. 용량 추가 상품은 실제 사용량을 보고 나중에
- 리소스(저장 비용)가 가장 중요(사용자 "제일 중요한게 리소스") → 97: 이미 작은 사진은 다시 저장하지 않음
- 고침(2026-10-29, 사용자가 보여 준 패밀리앨범 요금표·후기, research/pricing-2026-10.md 끝): 패밀리앨범도 가족 접속 기록('근황')·시기별 보기가 있다 → 1 보신 기록과 98은 차별점이 아니라 기본. 차별점은 '조부모 설치 없이' + 무료 화질(그쪽은 고화질 영상이 Pro ₩11,900). 스위피 무료가 그쪽 유료 수준이라 무료에서 무엇을 줄일지는 사용자 결정으로 남김
- 새 순서: 97 작은 사진 그대로 → 98 나이별 건너뛰기(추천) → 음성 한마디(받아 적기는 브라우저 무료 기능, 안 되는 브라우저는 녹음만·직접 쓰기) → 플러스 용량·결제 → 액자 모드

### 95. feature/view-log — 할머니가 보신 걸 엄마아빠에게 (진행 중, 경쟁력 기능 1)
- 요구(94, 사용자 "기능 구현 웹으로 먼저"): 가족이 사진을 본 걸 엄마아빠가 안다. 범위(사용자 2026-10-29 "추천대로"): **이름만**. 횟수·시간·주간 요약은 뺌(감시처럼 읽히고 덜 본 사람이 비교됨). 카톡의 1이 사라지는 것과 같은 역할이라 무료 기능(94의 '보신 기록 자세히' 플러스 항목은 지움)
- 디자인(캔버스 ParentViewViewers): 엄마아빠 크게 보기 날짜 줄 아래 눈 그림 + "외할머니·외할아버지가 봤어요"(셋 넘으면 이름 셋 + "외 N명"). 본 사람이 없으면 줄 없음
- DB(새 마이그레이션, 운영 적용 전 사용자 확인): `views`(사진·구성원, 처음 본 때) 한 사람 한 사진 한 줄. 가족 기기가 부르는 `sp_note_views(사진 id 배열)`(볼 수 있는 사진만, 승인된 구성원만), 엄마아빠가 부르는 `sp_parent_media_viewers(사진 id)`(본 사람 이름, 처음 본 순). 엄마아빠 계정은 안 셈
- 가족 화면: 눌러서 연 크게 보기는 페이지를 그릴 때 서버가 기록. 크게 보기에서 옆으로 넘긴 사진(영상 칸·창 끝 이동은 페이지를 열 때 기록)과 넘겨 보기 앨범은 가운데 카드에 1.5초 머물면 `/api/views`로 보냄(스크립트 없으면 크게 보기를 열 때만)
- 알림: 가족 입장 화면('누구세요?') 안내 아래 "엄마아빠에게 누가 봤는지 보여요" 한 줄

### 96. feature/bottom-bar — 주요 버튼 아래 고정·올리기 진행 칸 (완료, 0.5.1)
- 요구(사용자 2026-10-29): "하단 버튼 픽스드 되면 좋을 버튼들은 처리, 사파리 하단 바 고려" / "올리기 하단 프로그래스바 없애고 업로드중 숫자 영역이 프로그래스바"
- 고정: 처음 설정 다음·시작하기, 소개 다음, 올리기(버튼 둘), 문자 공유 링크 만들기(탭바 위), 가족 비밀번호 들어가기. 안 함: 바로 저장되는 화면 저장(스크립트 있으면 숨음), 내보내기·탈퇴 같은 위험 버튼
- 사파리: viewport-fit=cover + env(safe-area-inset-bottom). iPhone 17 Pro 시뮬레이터 iOS 26 사파리에서 떠 있는 아래 바 바로 위에 놓임 확인
- 넓은 올리기 화면은 오른쪽 칸 제자리, 높이 30rem 미만은 고정 풀림(막대가 화면 절반을 가리지 않게). 올리기 시작할 때 상태 칸을 한 번 보이게 스크롤
- 검사: tools/e2e/bottombar.py

### 97. feature/keep-small-photo — 이미 작은 사진은 다시 줄이지 않기 (완료, 0.5.2)
- 요구(사용자 2026-10-29): "화질이 너무 저하되면 안되니까 … 아예 큰 원본의 경우는 줄이되 이미 줄어있는 사진은 줄이지 않는 걸로", "제일 중요한 게 리소스"
- 원인: 영상은 이미 짧은 변 1080·5Mbps 이하면 그대로 올림. 사진은 크기와 상관없이 전부 캔버스로 다시 저장(긴 변 2048, JPEG 85%) → 카톡으로 받은 사진처럼 이미 줄인 JPEG는 한 번 더 화질이 깎이고, 낮은 화질 JPEG를 85%로 다시 저장하면 오히려 커지기도 함
- 규칙(올리기 화면 `photo()`): JPEG이고 긴 변 2048 이하면 원본에서 위치·기기 정보(APP1 EXIF·XMP, 다른 APP·주석, 끝에 붙은 데이터)를 화질 손실 없이 잘라 낸 파일과 다시 저장한 파일 중 **작은 쪽**을 보기용으로(같으면 원본). 회전 정보가 있는 사진(Orientation≠1)·깨진 파일·HEIC·PNG·WebP·큰 사진은 지금처럼 다시 저장. 색 정보(ICC)·Adobe 표시는 남김. 썸네일은 그대로 캔버스
- 구현: `src/lib/exif.ts`에 `stripJpeg(buf)`(바이트만 다룸, 단위 검사), `src/pages/upload.astro` `photo()`에서 고르기. 서버·DB 바뀜 없음
- 예상 결과: 카톡 사진은 화질 그대로·용량은 같거나 줄어듦. 큰 사진은 지금과 같음. 위치 정보는 어떤 경우에도 안 올라감
- 결과: 검토 3회(타입 오류·프로그레시브 스캔 사이 표지·길이 없는 표지·LONG 회전 값·JPEG 아닌 파일 통째 읽기·APP0 JFXX 반영). 단위 검사 38개, 실제 사진 20개(아이폰 원본·sips HEIC 변환·프로그레시브·CMYK·ICC·재시작 표지 등) 그림 동일·정보 없음, 화면 검사 tools/e2e/keepsmall.py 크롬·사파리 엔진(`webkit` 인자) 통과. 사파리는 다시 저장할 때 자기 작은 EXIF(해상도)를 붙임(원본 정보 아님). 알려진 차이: 원본 그대로 올린 넓은 색(P3) 사진은 썸네일(캔버스, sRGB)과 색이 조금 다를 수 있음. 아이폰 HDR 게인맵은 빠짐(다시 저장할 때도 같음). 실제 아이폰 사파리 확인은 사용자 쪽
- 범위 밖: 화질 85% 올리기(리소스 우선이라 안 함), 3분 넘는 영상 원본 그대로 올리기(최대 2GB, 리소스 구멍 → 다음 이슈 후보), WebP 메타데이터 자르기

### 98. 아이 나이별로 건너뛰기 (계획, 97 다음)
- 요구(사용자 2026-10-29, 다른 앱 화면을 보여 주며 "이런 필터도 좋겠다"): 앨범에서 오늘·만 2~3세·만 1~2세·만 0~1세·태어나기 전처럼 아이 나이 구간으로 바로 이동
- 제안: 엄빠 홈과 가족 앨범 둘 다. 사진 있는 구간만. 아이를 하나 고른 상태면 나이 구간(아이 생일 기준), '모두'면 연도. 0~1세는 백일·돌로 더 나눌지 디자인 때 정함
- 구현 방향: 이미 있는 '그 시점부터 불러오기'(`?before=<찍은 날~id>`, 34)를 구간 경계 날짜로. 목록은 네이티브 펼침(details)이나 링크 목록(손으로 만든 떠 있는 메뉴 안 씀), 스크립트 없어도 링크로 동작
- 순서: 디자인 캔버스 보드 먼저 → 계획 자세히 → 개발. 그림을 그대로 베끼지 않고 스위피 디자인 시스템으로

### 99. feature/wait-photos — 승인 대기 화면에 받은 사진 보여 주기 (완료, 0.5.5)
- 요구(사용자 2026-10-29 "먼저 고치기"): 기억하신 규칙 '승인 안 받은 사람은 받은 링크의 사진만'이 화면에 없음
- 원인: DB는 이미 됨(`sp_can_view_media`: 승인 대기 구성원은 들어온 링크의 `share_media`만, rls.sql '승인 전엔 공유 묶음 2장만'). 올리기 화면이 만든 링크엔 방금 올린 사진이 묶임(`/api/shares` mediaIds). 그런데 /wait는 글('지금은 받은 사진만 볼 수 있어요')만 있고 사진을 안 그림, 앨범은 대기면 /wait로 보냄. mock은 공유 묶음 규칙을 흉내 내지 않음
- 화면(/wait, 대기 상태일 때만): 안내 상자 아래 '받은 사진 N장' + 사진을 한 줄에 한 장 크게(원래 모양, 영상은 기본 재생 막대). 누르기·반응·한마디·저장 없음(승인 전이라 DB도 막음). 스크립트 0KB 유지
  - 묶음이 비었으면(설정에서 만든 그룹·문자 링크) 사진 칸 없이 글을 '엄마아빠가 확인하면 사진을 볼 수 있어요'로
  - 비밀번호 10번 틀림(기기 대기)은 지금처럼 사진 없음(DB가 기기 대기는 안 보여 줌)
- 구현: /wait에서 `listMedia(pass, { familyId: 대기 가족방, limit: 200 })`(RLS가 묶음만 줌) → 서명 주소. mock: 공유에 사진 id를 담고, 새 이름 대기 구성원은 들어온 공유의 사진만 보이게(DB와 같게)
- 디자인: 캔버스 새 보드 WaitPhotos(라이트·다크) 먼저
- 검사: e2e(엄빠 올리기 → 링크 → 새 이름 → 대기 화면에 그 사진만, 다른 사진 안 보임, 빈 묶음 글), 기존 entry 검사
- 결과: 검토 3회(못 불러오면 '불러오지 못했어요' 안내, 크기 모르는 것만 4:3 자리, 영상 섞이면 '사진·영상 N개', 대체 글 순번, mock 공유도 다른 가족방 사진은 거절). tools/e2e/waitphotos.py 크롬·사파리 엔진(`webkit` 인자), entry·bottombar·members·groups·family e2e, DB 검사(거절 63) 통과. 디자인 WaitPhotos v180. 남은 것: 영상 섞인 묶음·불러오기 실패는 e2e 없음(코드로만), 실제 아이폰·실제 DB 화면 확인은 안 함
