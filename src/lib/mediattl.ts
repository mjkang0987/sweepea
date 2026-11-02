// 서명된 사진 주소의 만료(부수 효과 없음, signed.ts가 쓰고 단위 검사로 본다)
// 135(사용자 2026-11-02 "3시간(최대 6시간)로 절충"): 3시간 단위로 맞춰 3시간 동안 같은 주소(브라우저 캐시를 오래 씀), 만료까지 3~6시간.
// 대가: 기기를 막거나 사진을 그룹에서 빼거나 가족방을 닫아도 이미 받은 주소는 만료(최대 6시간)까지 열린다(예전 최대 2시간). 지운 사진은 파일이 지워져 안 열림
const HOUR = 3600;
export const BUCKET = 3 * HOUR;
export const TTL = 6 * HOUR;

/** 지금 서명할 주소의 만료 시각(초) */
export const expiryOf = (nowMs: number) => Math.floor(nowMs / 1000 / BUCKET) * BUCKET + TTL;

/** 만료까지 남은 초. 지났거나 TTL보다 멀면(만들 수 없는 만료) 0 */
export function leftOf(exp: number, nowMs: number): number {
  const left = exp - Math.floor(nowMs / 1000);
  return Number.isInteger(exp) && left > 0 && left <= TTL ? left : 0;
}
