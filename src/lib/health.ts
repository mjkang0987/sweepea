// 접종·검진 일정(국가 권장 시기). 2026-10-26 확인: 질병관리청 표준 예방접종 일정(보건소 게시본, 2026-01-05 수정)과
// 영유아 건강검진 1~8차. 원문 대조는 plan.md '확인 필요'. 인플루엔자(매년)·HPV(성별 정보 없음)·구강검진·유료 백신은 뺐다.
// "A~B개월"은 A개월이 되는 날부터 B개월 마지막 날까지(B+1개월이 되기 전날)로 읽는다. 끝이 없는 항목(예: 2개월)은 그날부터 "지금 가능"

export type HealthKind = 'vaccine' | 'checkup';
interface Age { m?: number; d?: number }
export interface HealthItem {
  key: string;
  kind: HealthKind;
  name: string;
  /** 권장 시기 글(화면에 그대로) */
  age: string;
  from: Age;
  /** 이날부터는 시기 지남(없으면 지나지 않음) */
  until?: Age;
  /** 앞 접종을 한 날부터 센다(그 전엔 보이지 않음) */
  after?: { key: string; gap: Age };
}

const v = (key: string, name: string, age: string, from: Age, until?: Age): HealthItem => ({ key, kind: 'vaccine', name, age, from, until });
const c = (n: number, age: string, from: Age, until: Age): HealthItem => ({ key: `check-${n}`, kind: 'checkup', name: `영유아 건강검진 ${n}차`, age, from, until });
const range = (a: number, b: number) => ({ from: { m: a }, until: { m: b + 1 } });

export const HEALTH_ITEMS: HealthItem[] = [
  v('hepb-1', 'B형간염 1차', '출생 시', { d: 0 }),
  v('bcg', '결핵(BCG)', '생후 4주 이내', { d: 0 }, { d: 28 }),
  v('hepb-2', 'B형간염 2차', '1개월', { m: 1 }),
  ...[1, 2, 3].flatMap((n) => {
    const m = n * 2;
    return [
      v(`dtap-${n}`, `DTaP ${n}차`, `${m}개월`, { m }),
      v(`ipv-${n}`, `폴리오 ${n}차`, `${m}개월`, { m }),
      v(`hib-${n}`, `Hib ${n}차`, `${m}개월`, { m }),
      v(`pcv-${n}`, `폐렴구균 ${n}차`, `${m}개월`, { m }),
      // 로타: 1차는 생후 14주 6일까지, 2·3차는 8개월 0일 전까지 지원(보건소 게시본). 3차는 3회 접종 제품만
      v(`rv-${n}`, `로타바이러스 ${n}차${n === 3 ? '(3회 접종 제품만)' : ''}`, `${m}개월`, { m }, n === 1 ? { d: 105 } : { m: 8 }),
    ];
  }),
  v('hepb-3', 'B형간염 3차', '6개월', { m: 6 }),
  v('hib-4', 'Hib 4차', '12~15개월', range(12, 15).from, range(12, 15).until),
  v('pcv-4', '폐렴구균 4차', '12~15개월', range(12, 15).from, range(12, 15).until),
  v('mmr-1', 'MMR 1차', '12~15개월', range(12, 15).from, range(12, 15).until),
  v('var', '수두', '12~15개월', range(12, 15).from, range(12, 15).until),
  v('hepa-1', 'A형간염 1차', '12~23개월', range(12, 23).from, range(12, 23).until),
  // 2차 간격은 제품마다 달라(확인 필요) 1차를 체크한 날 6개월 뒤부터, 끝 없이
  { ...v('hepa-2', 'A형간염 2차', '1차 6개월 뒤부터', { m: 18 }), after: { key: 'hepa-1', gap: { m: 6 } } },
  v('je-1', '일본뇌염 1차', '12~23개월', range(12, 23).from, range(12, 23).until),
  v('je-2', '일본뇌염 2차(불활성화)', '12~23개월', range(12, 23).from, range(12, 23).until),
  v('dtap-4', 'DTaP 4차', '15~18개월', range(15, 18).from, range(15, 18).until),
  v('je-3', '일본뇌염 3차(불활성화) · 생백신 2차', '24~35개월', range(24, 35).from, range(24, 35).until),
  v('dtap-5', 'DTaP 5차', '4~6세', { m: 48 }, { m: 84 }),
  v('ipv-4', '폴리오 4차', '4~6세', { m: 48 }, { m: 84 }),
  v('mmr-2', 'MMR 2차', '4~6세', { m: 48 }, { m: 84 }),
  v('je-4', '일본뇌염(불활성화) 4차', '6세', { m: 72 }, { m: 84 }),
  v('tdap', 'Tdap 6차', '11~12세', { m: 132 }, { m: 156 }),
  v('je-5', '일본뇌염(불활성화) 5차', '12세', { m: 144 }, { m: 156 }),
  c(1, '생후 14~35일', { d: 14 }, { d: 36 }),
  c(2, '4~6개월', range(4, 6).from, range(4, 6).until),
  c(3, '9~12개월', range(9, 12).from, range(9, 12).until),
  c(4, '18~24개월', range(18, 24).from, range(18, 24).until),
  c(5, '30~36개월', range(30, 36).from, range(30, 36).until),
  c(6, '42~48개월', range(42, 48).from, range(42, 48).until),
  c(7, '54~60개월', range(54, 60).from, range(54, 60).until),
  c(8, '66~71개월', range(66, 71).from, range(66, 71).until),
];

/** 생일(YYYY-MM-DD)에 개월·일을 더한 날. 달 끝은 그달 마지막 날로(1월 31일 + 1개월 = 2월 28/29일) */
export function addAge(birth: string, age: Age): string {
  const [y, m, d] = birth.split('-').map(Number);
  const months = m - 1 + (age.m ?? 0);
  const ty = y + Math.floor(months / 12);
  const tm = ((months % 12) + 12) % 12;
  const last = new Date(Date.UTC(ty, tm + 1, 0)).getUTCDate();
  const base = Date.UTC(ty, tm, Math.min(d, last));
  return new Date(base + (age.d ?? 0) * 86_400_000).toISOString().slice(0, 10);
}

export type HealthState = { kind: 'soon'; from: string } | { kind: 'now' } | { kind: 'late' };

/** 오늘(YYYY-MM-DD) 기준 상태 */
export function healthState(item: HealthItem, birth: string, today: string): HealthState {
  const from = addAge(birth, item.from);
  if (today < from) return { kind: 'soon', from };
  if (item.until && today >= addAge(birth, item.until)) return { kind: 'late' };
  return { kind: 'now' };
}

/** 안 한 일정을 둘로: 다가오는 것(6개월 안에 시작, 지금 가능한 것 포함)과 지난 것(시기 지남, 또는 끝이 없는데 시작한 지 2개월 넘음).
 *  처음 쓰는 부모가 이미 한 접종을 다 체크하지 않아도 다가오는 일정이 지난 것에 묻히지 않게 한다. 시작일 순 */
export function splitSchedule(birth: string, today: string, done: Map<string, string>) {
  const horizon = addAge(today, { m: 6 });
  const stale = addAge(today, { m: -2 });
  const rows = HEALTH_ITEMS.filter((i) => !done.has(i.key) && (!i.after || done.has(i.after.key)))
    .map((i) => {
      if (!i.after) return { item: i, start: addAge(birth, i.from), state: healthState(i, birth, today) };
      // 앞 접종 날부터 센다: 그 날을 생일 자리에 넣어 계산
      const base = done.get(i.after.key)!;
      const item = { ...i, from: i.after.gap };
      return { item: i, start: addAge(base, i.after.gap), state: healthState(item, base, today) };
    })
    .filter((x) => x.start <= horizon)
    .sort((a, b) => (a.start === b.start ? 0 : a.start < b.start ? -1 : 1));
  // 앞 접종에 맞춘 항목은 오래돼도 다가오는 일정에 둔다
  const isPast = (x: (typeof rows)[number]) => x.state.kind === 'late' || (x.state.kind === 'now' && !x.item.until && !x.item.after && x.start < stale);
  return { upcoming: rows.filter((x) => !isPast(x)), past: rows.filter(isPast) };
}
