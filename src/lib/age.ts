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

/** 지난 시간: "방금", "10분 전", "3시간 전", 하루 넘으면 seenLabel("어제", "3일 전") */
export function agoLabel(iso: string, nowMs: number): string {
  const min = Math.floor((nowMs - Date.parse(iso)) / 60_000);
  if (min < 1) return '방금';
  if (min < 60) return `${min}분 전`;
  if (min < 24 * 60) return `${Math.floor(min / 60)}시간 전`;
  return seenLabel(iso, nowMs);
}

const NTH = ['첫', '두 번째', '세 번째', '네 번째', '다섯 번째', '여섯 번째', '일곱 번째', '여덟 번째', '아홉 번째', '열 번째'];

/** 오늘이 백일·돌·생일이면 레이어 제목 뒷부분("태어난 지 100일이에요"), 아니면 null. 태어난 날이 1일째(서울 날짜)
 * shortcut: 2월 29일생은 평년엔 생일 없음, 필요하면 2월 28일로 */
export function milestone(birth: string, today: string): string | null {
  if (Math.round((Date.parse(today) - Date.parse(birth)) / 86_400_000) + 1 === 100) return '태어난 지 100일이에요';
  const years = Number(today.slice(0, 4)) - Number(birth.slice(0, 4));
  if (years < 1 || today.slice(5) !== birth.slice(5)) return null;
  return `${NTH[years - 1] ?? `${years}번째`} 생일이에요`;
}
