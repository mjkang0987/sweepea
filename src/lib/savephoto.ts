// 사진 한 장 저장(사용자 2026-10-29 "사진 저장 누르니까 다운로드로 가는데, 앨범으로 가는 게 맞는데", "모바일이 중요해"):
// 휴대폰은 공유 창('이미지 저장')으로 사진 앱 앨범에, PC는 지금처럼 내려받기.
// 공유 창은 누른 바로 그때(사용자 동작 직후)만 열려서, 파일을 받느라 늦으면 휴대폰이 막는다(실기기 2026-10-29 "다운로드로 들어가는디").
// 그래서 사진은 화면을 열 때 미리 받아 두고, 아직 덜 받았거나 막히면 내려받기로 넘기지 않고 '한 번 더 눌러 주세요'
import { toast } from './copy';

const files = new Map<string, Promise<File>>();
const ready = new Map<string, File>();
const load = (href: string, name: string) => {
  if (!files.has(href)) {
    const p = fetch(href, { credentials: 'same-origin' }).then(async (r) => {
      if (!r.ok) throw new Error(String(r.status));
      const b = await r.blob();
      const f = new File([b], name, { type: b.type });
      ready.set(href, f);
      return f;
    });
    p.catch(() => files.delete(href));
    files.set(href, p);
  }
  return files.get(href)!;
};
const download = (a: HTMLAnchorElement) => {
  const link = Object.assign(document.createElement('a'), { href: a.href, download: a.download });
  document.body.appendChild(link);
  link.click();
  link.remove();
};

/** selector: download 속성이 있는 저장 링크. data-kind="photo"면 화면을 열 때 미리 받는다(영상은 커서 누르기 시작할 때) */
export function wireSave(selector: string) {
  // 손가락으로 쓰는 휴대폰만(PC는 지금처럼 내려받기가 편함)
  if (typeof navigator.canShare !== 'function' || !matchMedia('(pointer: coarse)').matches) return;
  const warm = (a: HTMLAnchorElement) => void load(a.href, a.download || 'sweepea').catch(() => {});
  for (const a of document.querySelectorAll<HTMLAnchorElement>(selector)) if (a.dataset.kind === 'photo') warm(a);
  document.addEventListener('pointerdown', (e) => {
    const a = (e.target as Element).closest<HTMLAnchorElement>(selector);
    if (a) warm(a);
  });
  document.addEventListener('click', (e) => {
    const a = (e.target as Element).closest<HTMLAnchorElement>(selector);
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    const file = ready.get(a.href);
    // 아직 받는 중: 기다리지 않는다(기다리면 공유 창이 막힘). 받으면 다시 누르게
    if (!file) {
      toast('사진을 준비하고 있어요. 잠깐 뒤 한 번 더 눌러 주세요.', a);
      load(a.href, a.download || 'sweepea').then(
        () => toast('준비됐어요. 저장을 한 번 더 눌러 주세요.', a),
        () => download(a),
      );
      return;
    }
    // 이 파일을 공유 못 하는 휴대폰이면 예전처럼 내려받기
    if (!navigator.canShare({ files: [file] })) return download(a);
    // 공유 창은 이 클릭 안에서 바로 연다(await 앞에 다른 기다림 없음)
    navigator.share({ files: [file] }).catch((err) => {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      if (err instanceof DOMException && err.name === 'NotAllowedError') return void toast('저장을 한 번 더 눌러 주세요.', a);
      download(a);
    });
  });
}
