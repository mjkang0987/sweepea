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

/** 지울 시각까지 남은 시간: "2일 5시간 남았어요", 하루 미만 "5시간 남았어요", 1시간 미만(또는 알 수 없음) "곧 지워져요". 시간은 내림 */
export function remainingLabel(untilMs: number, nowMs: number): string {
  const hours = Math.floor((untilMs - nowMs) / 3_600_000);
  if (!(hours >= 1)) return '곧 지워져요';
  const d = Math.floor(hours / 24);
  const h = hours % 24;
  return `${d ? `${d}일` : ''}${d && h ? ' ' : ''}${h ? `${h}시간` : ''} 남았어요`;
}

/** 마지막으로 본 때(서울 날짜 기준): "오늘", "어제", "3일 전" */
export function seenLabel(iso: string, nowMs: number): string {
  const day = (ms: number) => Date.parse(new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul' }).format(new Date(ms)));
  const days = Math.round((day(nowMs) - day(Date.parse(iso))) / 86_400_000);
  return days <= 0 ? '오늘' : days === 1 ? '어제' : `${days}일 전`;
}
