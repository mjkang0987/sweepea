// 아이마다 다음 접종·검진 하나(알림 탭 '다가오는 일정', 설정 › 아이 줄). 옆 기능이라 못 불러오면 그 아이만 뺀다
import type { Backend, Pass } from './backend';
import { nextOf } from './health';
export { monthDay } from './health';

type Kid = { id: string; name: string; birth_date: string };
export interface KidNext {
  id: string;
  name: string;
  /** 'DTaP 4차 접종' 같은 이름, 없으면 null(6개월 안에 없음) */
  what: string | null;
  /** 'YYYY-MM-DD'부터 가능, 이미 가능하면 null */
  from: string | null;
  /** 오늘부터 며칠 남았는지(이미 가능하면 0) */
  inDays: number;
}

export async function nextHealth(b: Backend, pass: Pass, kids: Kid[], today: string): Promise<KidNext[]> {
  const rows = await Promise.all(
    kids.map(async (k) => {
      const done = await b.healthDone(pass, k.id).catch(() => null);
      if (!done) return null;
      return { id: k.id, name: k.name, ...nextOf(k.birth_date, today, new Map(done.map((d) => [d.item_key, d.done_on]))) };
    }),
  );
  return rows.filter((x) => x !== null);
}
