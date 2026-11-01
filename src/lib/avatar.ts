// 가족 캐릭터(110): 그림 번호 1~45(public/avatar/<n>.webp, 96px). null = 안 고름(이름 첫 글자)
export const AVATARS = Array.from({ length: 45 }, (_, i) => i + 1);
export const avatarSrc = (n: number) => `/avatar/${n}.webp`;

/** 폼 값 → 번호. '' = 고르지 않음(null), 1~45 밖이거나 숫자가 아니면 undefined(잘못 보냄) */
export function parseAvatar(v: unknown): number | null | undefined {
  if (v === '') return null;
  const n = typeof v === 'string' && /^[0-9]{1,2}$/.test(v) ? Number(v) : NaN;
  return n >= 1 && n <= 45 ? n : undefined;
}

/** 고르지 않았을 때 동그라미 글자: 이름 마지막 낱말 첫 글자('하린 아빠' → 아) */
// 글자 단위로(이모지를 반쪽으로 자르지 않게)
export const initialOf = (name: string) => [...(name.split(' ').at(-1) || name)][0] ?? '';
