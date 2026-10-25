# index.md

스위피(Sweepea) 웹. 부모가 올린 아이 사진을 조부모·친척이 카톡 링크로 설치 없이 보는 가족 공유 앨범. 이 문서가 프로젝트 구조와 현재 상태의 기준이다. 작업 계획은 `plan.md`.

## 현재 상태

- 버전 0.1.0. DB 스키마·권한(Supabase 마이그레이션)은 작성·로컬 검사 완료, 실제 Supabase 프로젝트는 아직 없다.
- 사진 올리기 API(`/api/media`, Worker가 R2에 직접 저장)와 사진 전달(`/m/<키>`, 서명된 1~2시간 주소) 완료. 올리기 화면은 아직.
- 조부모 앨범(`/album` 넘겨 보기·모아 보기, `/album/<id>` 크게 보기, 집 고르기)과 하트·반응·한마디(폼 POST, `sp_react`·`sp_comment`) 완료.
- 가족 입장 화면(링크 → 누구세요 → 비밀번호 → 앨범·승인 대기·안내) 완료. mock 백엔드로 동작 확인, 앨범은 자리만. 기기 하나로 여러 가족방에 들어간다(가족방마다 승인·차단 따로). 다음 이슈는 plan.md 참고.
- 첫 화면(`/`)은 심볼과 이름만 있는 임시 페이지. 클라이언트 JS 0KB.
- 로컬 Lighthouse(모바일, 기본 스로틀링): LCP 약 0.7초, CLS 0, 접근성 100점.

## 기술

| 영역 | 선택 |
| --- | --- |
| 웹 | Astro 7 서버 렌더링(`output: 'server'`), 필요한 곳만 바닐라 JS |
| 배포 | Cloudflare Workers (`@astrojs/cloudflare`, `wrangler.jsonc`) |
| 백엔드 | Supabase (Postgres·Auth), 사진은 Cloudflare R2(바인딩 `MEDIA`, 버킷 `sweepea-media`). 실제 프로젝트는 아직 없음 |
| 도메인 | sweepea.co.kr (가비아 등록, DNS는 Cloudflare) |
| Node | 24 (`.nvmrc`). Astro 7은 22.23.4 이상 필요 |

## 구조

```
astro.config.mjs        Astro + Cloudflare 어댑터 (Images 바인딩·세션 KV 안 씀)
wrangler.jsonc          Worker 이름·호환 날짜
lighthouserc.json       성능 예산 (LCP 1.8초, CLS 0.05, JS 비압축 50KB, 접근성 100점)
.github/workflows/      perf.yml: 타입 검사 → 빌드 → 성능 예산 (PR, dev 푸시)
public/favicon.svg      심볼 (시스템 테마에 맞춰 색 바뀜)
src/styles/tokens.css   디자인 토큰 (색·글자·간격·모서리·터치). 원본은 디자인 시스템 '스위피'
src/styles/base.css     문서 기본 스타일 (.sp-html, .sp-body, 포커스 링)
src/layouts/Base.astro  공통 HTML 뼈대 (lang=ko, theme-color)
src/layouts/Family.astro 가족 화면 뼈대 (글자 크기 쿠키 적용)
src/styles/family.css   가족 화면 공통 (.sp-f*)
src/lib/backend/        백엔드 계약(types.ts), supabase.ts(fetch로 Auth·RPC), mock.ts(개발용, 운영 금지)
src/lib/pass.ts         출입증 쿠키(sp_pass, httpOnly)·글자 크기 쿠키(sp_size)
src/lib/families.ts     가족방 상태 분류(들어감·승인 대기)
src/lib/media.ts        사진 파일 규칙(종류별 부분·형식·크기), R2 키
src/pages/api/media/    올리기 API: POST(행) → PUT <id>/<부분>(파일) → POST <id>/done(완료)
src/lib/signed.ts       사진 주소 서명·확인(HMAC, MEDIA_URL_SECRET)
src/pages/m/            사진·영상 전달(서명 확인 → R2, Range)
worker-configuration.d.ts  `npm run types`(wrangler types)로 만든 Worker 타입
src/pages/index.astro   주소 없이 온 경우 안내
src/pages/i/[code]/     누구세요(index) → 비밀번호(password)
src/pages/wait.astro    승인 기다림 / 500.astro
src/pages/album/        앨범(index: 넘겨 보기·모아 보기, [id]: 크게 보기). 쿼리 f(집)·v(보기)·z(칸)
src/lib/album.ts        앨범 쿼리 읽기·링크·목록 불러오기, 반응 수·반응 폼 처리
src/components/        ReactRow(반응 5개)·HeartToggle·SayForm(한마디)·Notice
src/lib/emoji.ts        반응 도트 이모지와 페이지당 한 번 넣는 sprite
supabase/migrations/    DB 스키마·RLS·권한 함수(sp_*)·입장 RPC. 실제 Supabase에 그대로 적용
supabase/tests/         로컬 Postgres 16으로 권한 시나리오 검사 (stub.sql: auth 흉내, rls.sql: 시나리오, run.sh)
```

## DB 요약

- 부모: Supabase Auth 사용자(가족방당 1명). 가족 기기: 익명 사용자(기기 하나 = 익명 사용자 하나, 가족방마다 `devices` 한 행). 배우자는 구성원 + 기기 올리기 권한.
- 가족은 `media`의 정해진 열만 읽는다(부모 사용자 id·원본 키·용량 제외, `select *` 불가).
- 가족방끼리는 서로 안 보인다. 부모도 기기 사용자 id(`auth_user_id`)는 못 읽는다(열 권한이라 `select *` 불가).
- 입장은 `sp_entry_info`(누구세요 화면 정보) → `sp_enter`(이름 + 그룹 비밀번호). 새 이름은 링크 72시간 안에만, 승인 대기 3일. 틀린 기록은 기기·그룹별(3번 30초, 10번 승인 대기)과 그룹 전체(1시간 20번·하루 30번이면 새 기기는 승인 대기).
- 공유 링크는 `sp_create_share`로만(8자 코드). 연결 표는 family_id 복합 FK로 같은 가족방끼리만.
- 사진 행은 `sp_create_media`로만 만들고, 상태·저장 키·용량은 서버(`sp_finish_upload`, service_role)만 쓴다. 비밀번호 해시는 클라이언트가 못 읽는다.

## 규칙

- CSS는 클래스·ID 선택자만. 태그 선택자 금지. 클래스 접두사 `sp-`.
- 테마는 기기 설정만 따른다. 색은 반드시 토큰 변수로.
- 네이티브 HTML 컨트롤 우선, 시맨틱 요소 우선, WCAG 2.2 AA.
- 성능 예산을 넘으면 머지하지 않는다.

## 명령

| 명령 | 하는 일 |
| --- | --- |
| `npm run dev` | 개발 서버 (`SWEEPEA_BACKEND=mock`이면 메모리 백엔드) |
| `npm run check` | 타입 검사 |
| `npm run types` | wrangler.jsonc 바인딩이 바뀌면 Worker 타입 다시 만들기 |
| `npm run build` | 빌드 (`dist/`) |
| `npm run test:db` | 로컬 Postgres 16 임시 클러스터에 마이그레이션 적용 후 권한 시나리오 검사 (`PG_BIN`으로 경로 지정) |
| `npm run perf` | 빌드 결과로 Lighthouse CI 예산 검사 (Chrome 필요, `CHROME_PATH`로 지정 가능) |
