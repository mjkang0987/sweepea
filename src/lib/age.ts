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

/** 오늘 나이 'N개월 N일'(앨범 머리, 사용자 2026-10-29 "아기 정보는 항상 노출, N개월 NN일"). 한 달 전이면 'N일', 딱 달이 차면 'N개월'.
 *  달 생일이 없는 달(31일생의 30일 달)은 그 달 마지막 날을 달 생일로. 태어나기 전이면 null */
export function ageLabel(birth: string, today: string): string | null {
  if (today < birth) return null;
  const [by, bm, bd] = birth.split('-').map(Number);
  const [ty, tm, td] = today.split('-').map(Number);
  // 달 수도 같은 규칙으로: 이번 달 생일(없으면 그 달 마지막 날)이 지났으면 한 달 참(1/31생은 2/28에 1개월, 리뷰 2026-10-29)
  const lastNow = new Date(Date.UTC(ty, tm, 0)).getUTCDate();
  const m = (ty - by) * 12 + (tm - bm) - (td < Math.min(bd, lastNow) ? 1 : 0);
  const y = by + Math.floor((bm - 1 + m) / 12), mo = (bm - 1 + m) % 12;
  const last = new Date(Date.UTC(y, mo + 1, 0)).getUTCDate();
  const anniv = Date.UTC(y, mo, Math.min(bd, last));
  const d = Math.round((Date.UTC(ty, tm - 1, td) - anniv) / 86_400_000);
  return m === 0 ? `${d}일` : d === 0 ? `${m}개월` : `${m}개월 ${d}일`;
}
