// 동의 기록(152): 종류마다 지금 버전(약관·처리방침 시행일). 약관을 바꾸면 여기 날짜를 올려 다시 동의를 받는다(terms.astro·privacy.astro의 EFFECTIVE와 같이)
import type { ParentHome } from './backend';

export const CONSENT = { terms: '2026-11-02', health: '2026-11-02' } as const;
export type ConsentKind = keyof typeof CONSENT;
/** 지금 버전에 동의했는가 */
export const hasAgreed = (home: Pick<ParentHome, 'agreed'>, kind: ConsentKind) => (home.agreed ?? []).includes(`${kind}:${CONSENT[kind]}`);
