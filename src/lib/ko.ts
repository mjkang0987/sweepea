/** 받침이 있으면 true (한글 음절만 본다) */
export function hasBatchim(word: string): boolean {
  const code = word.trim().charCodeAt(word.trim().length - 1) - 0xac00;
  return code >= 0 && code <= 11171 && code % 28 !== 0;
}

/** 아이 이름을 부르는 꼴: 하린 → 하린이, 도윤 → 도윤이, 서아 → 서아 */
export function callName(name: string): string {
  return hasBatchim(name) ? `${name}이` : name;
}

/** '(으)로': 받침 없거나 ㄹ 받침이면 '로', 그 밖의 받침이면 '으로' */
export function ro(word: string): string {
  const w = word.trim();
  const code = w.charCodeAt(w.length - 1) - 0xac00;
  const jong = code >= 0 && code <= 11171 ? code % 28 : 0;
  return `${w}${jong === 0 || jong === 8 ? '로' : '으로'}`;
}
