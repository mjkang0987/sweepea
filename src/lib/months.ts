// 월별·연별 카드(98a·98c): 달 묶음을 해마다 합치기. 화면과 따로 검사하려고 순수 함수만
import type { MediaMonth } from './backend/types';

/** 연별 카드(98c): 달 묶음을 해마다 합침. 대표 5장은 최근 달부터 달마다 1번 대표, 모자라면 2번·3번(DB 새 함수 없이).
 *  last = 그 해 가장 최근 달(누르면 그 달부터) */
export function groupYears(months: MediaMonth[]): { y: string; n: number; from: number; to: number; last: string; reps: MediaMonth['reps'] }[] {
  const out: { y: string; n: number; from: number; to: number; last: string; ms: MediaMonth[] }[] = [];
  for (const mo of months) {
    const y = mo.ym.slice(0, 4), m = Number(mo.ym.slice(5));
    const cur = out.at(-1);
    if (cur?.y === y) {
      cur.n += mo.n;
      cur.from = m;
      cur.ms.push(mo);
    } else out.push({ y, n: mo.n, from: m, to: m, last: mo.ym, ms: [mo] });
  }
  return out.map(({ ms, ...g }) => {
    const reps: MediaMonth['reps'] = [];
    for (let k = 0; reps.length < 5 && ms.some((mo) => mo.reps[k]); k++) for (const mo of ms) if (mo.reps[k] && reps.length < 5) reps.push(mo.reps[k]);
    return { ...g, reps };
  });
}
