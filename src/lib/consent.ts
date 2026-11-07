// 동의 기록(152): 종류마다 지금 버전(약관·처리방침 시행일). 약관을 바꾸면 여기 날짜를 올려 다시 동의를 받는다(terms.astro·privacy.astro의 EFFECTIVE와 같이)
import type { ParentHome } from './backend';

// terms 2026-11-03: 처리방침 국외 이전 항목 채움·약관 책임 조항 고침(154) → 엄빠에게 다시 동의를 받음
// terms 2026-11-05: 처리방침에 방문마다 시각·머문 시간·연 화면 이름을 남기는 것(179) → 엄빠에게 다시 동의를 받음
// terms 2026-11-06: 약관 제3조 승인 문구를 실제대로(새 이름만 승인, 승인 전엔 그 링크 사진만 보임, 182) → 엄빠에게 다시 동의를 받음
export const CONSENT = { terms: '2026-11-06', health: '2026-11-02' } as const;
export type ConsentKind = keyof typeof CONSENT;
/** 지금 버전에 동의했는가 */
export const hasAgreed = (home: Pick<ParentHome, 'agreed'>, kind: ConsentKind) => (home.agreed ?? []).includes(`${kind}:${CONSENT[kind]}`);
