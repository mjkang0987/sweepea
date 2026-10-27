# index.md

스위피(Sweepea) 웹. 부모가 올린 아이 사진을 조부모·친척이 카톡 링크로 설치 없이 보는 가족 공유 앨범. 이 문서가 프로젝트 구조와 현재 상태의 기준이다. 작업 계획은 `plan.md`.

## 현재 상태

- 버전 0.4.25(dev, 운영 주소에 자동 배포). main은 아직 첫 커밋(PR #1 열림). 운영 Supabase(서울)에 마이그레이션 16개 적용, 사진은 R2. 새 세션 인계는 plan.md 맨 위 '새 세션 인계'.
- 화면 반응 속도(0.4.11~): 크게 보기의 반응·한마디·지우기는 스크립트가 있으면 페이지 이동 없이 아래 판만 갈아 끼움(반응은 누르는 즉시 표시). 페이지 이동은 겹쳐 넘어감(`@view-transition`). 설정 › 가족(0.4.17~)도 승인·거절·내 가족 아님·링크 만들기를 그 자리에서(확인은 모달 레이어), 사진 정보 수정 저장(0.4.18~)도 그 자리에서 '저장했어요' 토스트, 홈 가운데 레이어(0.4.19~)는 모달로 뜨고 닫기·나중에는 그 자리에서(한 번에 하나씩 이어서), 가족 한 명(0.4.20~)은 올리기 허용 스위치 그 자리에서·내보내기 확인 레이어, 바로 저장 화면들(0.4.21~, 공용 `AutoSave`: 설정 스위치·글자 크기·아이 접종 보기·그룹)도 그 자리에서 + 토스트, 그룹 주소 보내기·다시 만들기(0.4.22~)는 그룹 화면에 링크 카드·확인 레이어, 접종은 체크하면 바로 저장(0.4.23~), 입력 화면 저장 버튼은 탭바 위 막대 고정(`.sp-p__savebar`, Parent `savebar`). 나머지 화면은 아직 폼 → 페이지 이동(다음 작업).
- 안내: 결과는 아래에서 떴다 사라지는 토스트(`src/components/Toast.astro`, 아이콘 없이 글자만, CSS는 base.css로 엄빠·가족 공통, 엄빠 탭 화면은 탭바 위). 한마디 시트가 열려 있으면 시트 위쪽 바깥에 뜸. 확인은 가운데 레이어(`.sp-layer`, 스크립트로 여는 건 `dialog.sp-layer__modal`) — 사진 지우기가 첫 번째.
- 사진 올리기 API(`/api/media`, Worker가 R2에 직접 저장)와 사진 전달(`/m/<키>`, 서명된 1~2시간 주소) 완료. 100MB 넘는 영상 원본은 `/api/media/<id>/multipart`로 50MB씩 나눠 올림(0.4.24~, 한 편 2GB). 완료 때도 무료 5GB 한도(마이그레이션 17, 운영 적용은 사용자 확인 뒤).
- 부모 올리기(`/upload`: 기기에서 줄이기(영상도 0.4.25~ mediabunny·WebCodecs로 짧은 변 1080·H.264 5Mbps, 3분 넘거나 못 하면 원본, 원본 보관 안 함 안내)·줄이기·올리기 진행률 %와 진행 막대·EXIF 찍은 날·대표 사진·아이·그룹, 올린 뒤 공유 링크 `POST /api/shares`) 완료. 부모 화면은 JS 사용, 가족 화면은 0KB 유지(예외: 크게 보기 `/album/[id]`만 작은 스크립트 — 영상 재생 막대·소리·옆으로 밀기, 없어도 ‹ › 링크·기본 재생 막대로 동작. 골라서 저장하기 `/album/save`도 작은 스크립트 — 고른 수·공유 창/내려받기, 없으면 고른 사진마다 저장 링크).
- 설정 > 가족(`/settings/family` 승인·거절·새 기기·그룹 링크 — 스크립트가 있으면 그 자리에서, `/settings/family/sms` 한 사람용 문자 링크) 완료.
- 설정: 구성원 상세(`/settings/family/member/<id>` 사진 올리기 허용·내보내기), 가족도 사진 저장하기(`/settings`, 켜면 가족 크게 보기에 저장 링크), 저장 용량(`/settings/storage`) 완료.
- 설정: 아이(`/settings/children` 목록, `/settings/children/<id|new>` 고치기·추가, 가족방당 10명), 가족 화면 글자 크기(`/settings/text-size`, 가족이 처음 들어올 때 크기 `families.text_size_mode`), 계정(`/settings/account` 제공자·로그아웃) 완료.
- PC 화면(64rem 이상): 가족 모아 보기·크게 보기 넓게(4·6·8칸), 부모 앨범 넓게·메뉴 위, 올리기 두 칸·끌어다 놓기 완료.
- 매일 정리 예약 작업(`src/worker.ts` scheduled, 서울 새벽 3:17): 탈퇴 기한 지난 가족방·하루 지난 올리기 지우기, R2 정리 대기열 폴더 지우기(`src/jobs/cleanup.ts`). 무료 가족방 5GB가 차면 새로 올리기만 멈춤 완료.
- 홈 화면에 두기: `public/manifest.webmanifest`·`public/icons/`(콩이), 가족 앨범 위 안내(`src/components/InstallGuide.astro`, 기기 판별 `src/lib/install.ts`), 앱 안 브라우저는 엄마아빠에게 부탁(`members.install_help_at`) → 부모 최근 반응 '도와줄 사람' 완료.
- 접종·검진(`/health/<아이 id>`, 앨범 위 아이별 다음 일정, 설정 > 아이에서 켜고 끄기): 일정 표 `src/lib/health.ts`, 완료 기록 `health_done`(부모만) 완료.
- 부모 최근 반응(`/reactions`, 앨범 위 '최근 반응 새 N'): 승인된 가족의 반응·한마디, 확인할 사람, 열면 읽음 완료.
- 부모 사진 정보(`/photo/<id>`, 크게 보기 '사진 정보 수정'에서): 찍은 날·아이·보여줄 그룹 고치기, 지우기(확인 레이어 → 용량 빼고 R2 정리 대기열 `r2_cleanup.prefix`) 완료. 찍은 날은 JPEG만 EXIF, 나머지는 파일 시각.
- 그룹 관리(`/settings/family/groups` 목록·추가(10개)·상세·비밀번호 바꾸기·주소 다시 만들기) 완료.
- 탈퇴하기(`/settings/account` 확인 체크, 구독 중이면 막음)·작별(`/goodbye`)·되살리기(`/restore`, 유예 중 부모 화면은 여기로, 남은 시간 안내) 완료. 3일 유예 뒤 실제 삭제는 예약 작업(13번, 출시 전 필수).
- 부모 시작(`/start` 소개, `/login`·`/auth/callback` OAuth PKCE, `/setup` 처음 설정, `/home` 앨범, `/settings` 자리) 완료. 부모 세션은 쿠키 `sp_parent`(가족 기기 `sp_pass`와 따로).
- 조부모 앨범(`/album` 넘겨 보기·모아 보기, `/album/<id>` 크게 보기, 집 고르기)과 하트·반응·한마디(폼 POST, `sp_react`·`sp_comment`) 완료.
- 크게 보기 한마디(0.4.1~): 판 안 한 줄(최근 한마디 말줄임 + 수) → 누르면 아래 시트(dialog, 스크립트 없으면 #talk로 판 안에). 반응은 수 붙은 알약 5개 한 줄(하트 따로 버튼 없음, 옛 브라우저 넘겨 보기 카드만 하트 하나). 볼 수 있는 사진이면 엄빠·승인된 가족 모두 봄(`sp_comment_list`, 승인 대기는 못 봄, 최근 100개, `mine`으로 내 것 표시). 쓴 사람만 지우기(`sp_delete_comment`, 휴지통 → 한 번 더 확인). 옛 `sp_media_comments`는 안 씀(지울 예정). 엄빠 사진 정보 수정 화면의 최근 한마디도 같은 목록 첫 줄.
- 가족 입장 화면(링크 → 누구세요 → 비밀번호 → 앨범·승인 대기·안내) 완료. 기기 하나로 여러 가족방에 들어간다(가족방마다 승인·차단 따로). 다음 이슈는 plan.md 참고.
- 첫 화면(`/`)은 심볼과 이름만 있는 임시 페이지. 클라이언트 JS 0KB.
- 로컬 Lighthouse(모바일, 기본 스로틀링): LCP 약 0.7초, CLS 0, 접근성 100점.

## 기술

| 영역 | 선택 |
| --- | --- |
| 웹 | Astro 7 서버 렌더링(`output: 'server'`), 필요한 곳만 바닐라 JS |
| 배포 | Cloudflare Workers (`@astrojs/cloudflare`, `wrangler.jsonc`) |
| 백엔드 | Supabase (Postgres·Auth), 사진은 Cloudflare R2(바인딩 `MEDIA`, 버킷 `sweepea-media`). 실제 프로젝트 `sweepea`(서울, 무료 조직, 마이그레이션 13개 적용). 실제로 개발하려면 `cp .dev.vars.supabase .dev.vars`(git 제외) |
| 도메인 | sweepea.co.kr (가비아 등록, DNS는 Cloudflare) |
| Node | 24 (`.nvmrc`). Astro 7은 22.23.4 이상 필요 |

## 구조

```
astro.config.mjs        Astro + Cloudflare 어댑터 (Images 바인딩·세션 KV 안 씀)
wrangler.jsonc          Worker 이름·호환 날짜·진입점(src/worker.ts)·매일 예약(crons)
src/worker.ts           Worker 진입점: 화면은 Astro 어댑터, scheduled는 정리 작업
src/jobs/cleanup.ts     매일 정리(가족방·올리는 중 사진·R2 폴더), 외부 호출 한도 안에서
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
src/pages/api/media/    올리기 API: POST(행) → PUT <id>/<부분>(파일, 큰 영상은 <id>/multipart 조각) → POST <id>/done(완료)
src/lib/signed.ts       사진 주소 서명·확인(HMAC, MEDIA_URL_SECRET)
src/pages/m/            사진·영상 전달(서명 확인 → R2, Range)
worker-configuration.d.ts  `npm run types`(wrangler types)로 만든 Worker 타입
src/pages/index.astro   주소 없이 온 경우 안내
src/pages/i/[code]/     누구세요(index) → 비밀번호(password)
src/pages/wait.astro    승인 기다림 / 500.astro
src/pages/album/        앨범(index: 넘겨 보기·모아 보기, [id]: 크게 보기). 쿼리 f(집)·v(보기)·z(칸)
src/lib/album.ts        앨범 쿼리 읽기·링크·목록 불러오기, 반응 수·반응 폼 처리
src/components/        Viewer(크게 보기, 가족·엄빠 공통. 반응·한마디·지우기는 스크립트가 있으면 페이지 이동 없이 판만 갈아 끼움)·ReactRow(반응 알약·수)·SayForm(한마디)·Toast(안내)·Notice
src/lib/parent.ts       부모 로그인 제공자·PKCE·부모 화면 진입(loadParent)
src/layouts/Parent.astro 부모 화면 뼈대(아래 탭), 스타일 src/styles/parent.css(.sp-p*)
src/lib/age.ts          생후 개월·생일·백일/돌/생일 당일·남은 시간·지난 시간 표시(단위 검사)
src/lib/layers.ts       가운데 레이어 '봤음' 기기 쿠키(들어오기 신청·승인·새 사진·백일/생일·저장 공간)
src/lib/health.ts       접종·검진 권장 일정 표와 날짜 계산(단위 검사)
src/lib/emoji.ts        반응 이모지(기기 기본 이모지 글자)·이름·움직임
supabase/migrations/    DB 스키마·RLS·권한 함수(sp_*)·입장 RPC. 실제 Supabase에 그대로 적용
supabase/tests/         로컬 Postgres 16으로 권한 시나리오 검사 (stub.sql: auth 흉내, rls.sql: 시나리오, run.sh)
tools/                  개발 도구: dev.sh(mock 개발 서버), e2e/(화면 흐름 검사 Playwright), design/·render/(디자인 보드 만들기·그려 보기). 쓰는 법은 plan.md '새 세션 인계'
```

## DB 요약

- 부모: Supabase Auth 사용자(가족방당 1명). 가족 기기: 익명 사용자(기기 하나 = 익명 사용자 하나, 가족방마다 `devices` 한 행). 배우자는 구성원 + 기기 올리기 권한.
- 가족은 `media`의 정해진 열만 읽는다(부모 사용자 id·원본 키·용량 제외, `select *` 불가).
- 가족방끼리는 서로 안 보인다. 부모도 기기 사용자 id(`auth_user_id`)는 못 읽는다(열 권한이라 `select *` 불가).
- 입장은 `sp_entry_info`(누구세요 화면 정보) → `sp_enter`(이름 + 그룹 비밀번호). 새 이름은 링크 72시간 안에만, 승인 대기 3일. 틀린 기록은 기기·그룹별(3번 30초, 10번 승인 대기)과 그룹 전체(1시간 20번·하루 30번이면 새 기기는 승인 대기).
- 내보낸(거절된) 구성원은 반응·한마디 기록이 있으면 지우지 않고 그 이름을 막는다(`sp_member_has_history`). 올리기 허용은 기기마다(`devices.can_upload`).
- 탈퇴: `sp_request_delete`가 `families.delete_after`(3일 뒤)를 정하면 가족 화면·올리기·공유가 바로 닫힌다. 되살리기 `sp_restore_family`, 지우기 `sp_purge_deleted_families`(service_role) → `r2_cleanup`에 R2 정리 대기.
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
| `npm run dev` | 개발 서버 (`SWEEPEA_BACKEND=mock`이면 메모리 백엔드, `SWEEPEA_MOCK_USED_BYTES`로 저장 사용량 미리 더하기) |
| `npm run check` | 타입 검사 |
| `npm run test:unit` | 순수 함수 단위 검사(`tests/*.test.ts`, Node 24 타입 제거 실행) |
| `npm run types` | wrangler.jsonc 바인딩이 바뀌면 Worker 타입 다시 만들기 |
| `npm run build` | 빌드 (`dist/`) |
| `npm run test:db` | 로컬 Postgres 16 임시 클러스터에 마이그레이션 적용 후 권한 시나리오 검사 (`PG_BIN`으로 경로 지정) |
| `npm run perf` | 빌드 결과로 Lighthouse CI 예산 검사 (Chrome 필요, `CHROME_PATH`로 지정 가능) |
| `bash tools/dev.sh` | mock 개발 서버(:4321, 백그라운드로). node가 낮으면 Node 24를 받아 씀 |
| `cd tools/e2e && python3 <이름>.py` | 화면 흐름 검사(개발 서버 필요), 끝줄 `FAILS []`면 통과 |
