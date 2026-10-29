// 사진 한 장 저장(사용자 2026-10-29 "사진 저장 누르니까 다운로드로 가는데, 앨범으로 가는 게 맞는데"):
// 휴대폰은 공유 창('이미지 저장')으로 사진 앱 앨범에, 공유 창이 없으면(PC) 지금처럼 내려받기.
// 공유 창은 누른 직후에 열어야 휴대폰이 막으므로 누르기 시작할 때 받아 둔다. 늦어서 막히면 예전처럼 내려받기
const files = new Map<string, Promise<File>>();
const load = (href: string, name: string) => {
  if (!files.has(href)) {
    const p = fetch(href, { credentials: 'same-origin' }).then(async (r) => {
      if (!r.ok) throw new Error(String(r.status));
      const b = await r.blob();
      return new File([b], name, { type: b.type });
    });
    p.catch(() => files.delete(href));
    files.set(href, p);
  }
  return files.get(href)!;
};

/** selector: download 속성이 있는 저장 링크 */
export function wireSave(selector: string) {
  // 손가락으로 쓰는 휴대폰만(PC는 지금처럼 내려받기가 편함)
  if (typeof navigator.canShare !== 'function' || !matchMedia('(pointer: coarse)').matches) return;
  const warm = (a: HTMLAnchorElement) => void load(a.href, a.download || 'sweepea').catch(() => {});
  // 누르기 시작할 때 받기 시작(화면에 보이는 사진과 같은 주소라 캐시에서 금방, 큰 영상을 미리 받지 않게 열 때는 안 받음)
  document.addEventListener('pointerdown', (e) => {
    const a = (e.target as Element).closest<HTMLAnchorElement>(selector);
    if (a) warm(a);
  });
  document.addEventListener('click', async (e) => {
    const a = (e.target as Element).closest<HTMLAnchorElement>(selector);
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    try {
      const file = await load(a.href, a.download || 'sweepea');
      if (!navigator.canShare({ files: [file] })) throw new Error('no share');
      await navigator.share({ files: [file] });
    } catch (err) {
      // 그만두기는 실패가 아님. 공유를 못 하면(파일 종류·권한) 예전처럼 내려받기
      if (err instanceof DOMException && err.name === 'AbortError') return;
      const link = Object.assign(document.createElement('a'), { href: a.href, download: a.download });
      document.body.appendChild(link);
      link.click();
      link.remove();
    }
  });
}
