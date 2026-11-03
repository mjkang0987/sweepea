// 뒤로 링크(150, 사용자 "이용약관·처리방침에서 뒤로 가기 없음"): 스크립트 없이 들어온 화면으로.
// 이 사이트는 referrer-policy가 no-referrer라 온 곳을 모른다 → 링크에 ?from=/login 처럼 붙여 받는다. 같은 사이트 경로만, 아니면 첫 화면
const SAFE = /^\/(?![\/\\])[\w\-./?=&%]*$/;
export function backHref(url: URL, fallback = '/'): string {
  const from = url.searchParams.get('from') ?? '';
  if (!SAFE.test(from)) return fallback;
  return new URL(from, url).pathname === url.pathname ? fallback : from;
}
/** 약관·처리방침으로 가는 링크: 지금 화면 경로를 from으로 */
export const docHref = (doc: '/terms' | '/privacy', from: string) => `${doc}?from=${encodeURIComponent(from)}`;
