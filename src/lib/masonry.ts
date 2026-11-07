// 엇갈린 배열(디자인 엄빠 앨범·GrandList, 부모 홈과 가족 모아 보기 2줄 공용): 사진을 차례로 지금 가장 짧은 줄에 쌓는다. 스크립트 없이 CSS 격자 자리로 내보낸다.
// 높이 단위는 줄 폭의 1/UNITS(화면 폭이 바뀌어도 비율 그대로). 칸마다 1단위를 더 차지하고, 실제 세로 간격은 CSS margin-bottom이 그 안에서 정한다
export const UNITS = 40;

/** 세로/가로 비율. 크기를 모르면 정사각, 너무 길거나 납작한 사진은 잘라서 보여 줄 만큼만 */
export function ratioOf(width: number | null | undefined, height: number | null | undefined): number {
  if (!width || !height) return 1;
  return Math.min(1.6, Math.max(0.6, height / width));
}

/** 줄 번호(1부터)·시작 칸(1부터)·차지하는 칸 수(간격 1칸 포함) */
export function masonry(ratios: number[], cols: number): { col: number; row: number; span: number }[] {
  const tops = Array<number>(cols).fill(1);
  return ratios.map((r) => {
    const col = tops.indexOf(Math.min(...tops));
    const span = Math.round(r * UNITS) + 1;
    const out = { col: col + 1, row: tops[col], span };
    tops[col] += span;
    return out;
  });
}
