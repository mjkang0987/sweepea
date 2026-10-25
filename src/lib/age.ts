/** 생후 개월(달력 기준, 그달 생일이 안 지났으면 한 달 덜). birth·today는 YYYY-MM-DD */
export function monthsOld(birth: string, today: string): number {
  const [by, bm, bd] = birth.split('-').map(Number);
  const [ty, tm, td] = today.split('-').map(Number);
  return Math.max(0, (ty - by) * 12 + (tm - bm) - (td < bd ? 1 : 0));
}

/** "2025년 9월 17일" */
export function birthLabel(birth: string): string {
  const [y, m, d] = birth.split('-').map(Number);
  return `${y}년 ${m}월 ${d}일`;
}

/** 지울 시각까지 남은 시간: "2일 5시간 남았어요", 하루 미만 "5시간 남았어요", 1시간 미만 "1시간 안에 지워져요". 시간은 내림 */
export function remainingLabel(untilMs: number, nowMs: number): string {
  const hours = Math.floor((untilMs - nowMs) / 3_600_000);
  if (hours < 1) return '1시간 안에 지워져요';
  const d = Math.floor(hours / 24);
  const h = hours % 24;
  return `${d ? `${d}일` : ''}${d && h ? ' ' : ''}${h ? `${h}시간` : ''} 남았어요`;
}
