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
