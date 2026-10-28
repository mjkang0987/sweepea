// 목록 화면 공통(브라우저): 아래로 내리면 다음 쪽 이어 붙이기, 크게 보기에서 닫고 돌아오면 보던 자리로

/** 목록 끝 [data-more] 안 '사진 더 보기' 링크가 화면에 가까워지면(600px 앞) 그 쪽을 받아 merge로 붙이고, 받은 쪽의 끝 줄로 바꾼다.
 * 못 받으면 링크를 되돌려 둔다(누르면 그 쪽 페이지로). 돌려주는 함수는 지금 바로 받기(옆으로 넘기는 목록은 스스로 부른다, observe: false).
 * IntersectionObserver가 없으면 링크 그대로 */
export function autoMore(merge: (doc: Document) => void, { observe = true } = {}): () => void {
  const io = observe && typeof IntersectionObserver === 'function' ? new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && void load(e.target as HTMLElement)), { rootMargin: '600px 0px' }) : null;
  let busy = false;
  const watch = () => {
    const el = document.querySelector<HTMLElement>('[data-more]');
    if (io && el?.querySelector('a')) io.observe(el);
  };
  async function load(el: HTMLElement) {
    io?.unobserve(el);
    const a = el.querySelector('a');
    if (!a || busy) return;
    busy = true;
    const wait = document.createElement('p');
    wait.className = 'sp-more__end';
    wait.setAttribute('role', 'status');
    wait.innerHTML = '<img class="sp-more__kongi" src="/kongi.svg" width="32" height="32" alt="" />사진 불러오는 중…';
    el.replaceWith(wait);
    try {
      const res = await fetch(a.href, { credentials: 'same-origin' });
      // 로그인이 풀리면 다른 화면으로 돌려보낸다
      if (res.redirected && new URL(res.url).pathname !== new URL(a.href).pathname) return void location.assign(res.url);
      if (!res.ok) throw new Error(String(res.status));
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      merge(doc);
      const end = doc.querySelector('[data-more]');
      if (end) wait.replaceWith(document.importNode(end, true));
      else wait.remove();
      watch();
    } catch {
      // 다시 저절로 받지는 않는다(끝없이 되풀이하지 않게). 누르면 그 쪽 페이지로
      wait.replaceWith(el);
      el.dataset.failed = '';
    } finally {
      busy = false;
    }
  }
  watch();
  return () => {
    const el = document.querySelector<HTMLElement>('[data-more]');
    if (el && !('failed' in el.dataset)) void load(el);
  };
}

const SPOT = 'sp-spot';
/** 칸 링크를 누를 때 그 칸의 화면 속 높이를 적어 두고, #c-<id>로 돌아오면 그 칸을 같은 높이에(모르면 가운데) 둔다 */
export function keepSpot(cellLink: string) {
  document.addEventListener('click', (e) => {
    const li = (e.target as Element).closest(cellLink)?.closest<HTMLElement>('[id^="c-"]');
    if (!li) return;
    try {
      sessionStorage.setItem(SPOT, JSON.stringify({ id: li.id, top: li.getBoundingClientRect().top }));
    } catch {
      // 저장소를 못 쓰면 가운데로
    }
  });
  const id = decodeURIComponent(location.hash.slice(1));
  const li = id.startsWith('c-') ? document.getElementById(id) : null;
  if (!li) return;
  let saved: { id?: string; top?: number } = {};
  try {
    saved = JSON.parse(sessionStorage.getItem(SPOT) ?? '{}');
    sessionStorage.removeItem(SPOT);
  } catch {
    saved = {};
  }
  // 브라우저가 #앵커로 먼저 옮긴 뒤(페이지를 다 읽은 뒤)에 맞춘다
  const place = () =>
    requestAnimationFrame(() => {
      if (saved.id === id && typeof saved.top === 'number') window.scrollTo(0, window.scrollY + li.getBoundingClientRect().top - saved.top);
      else li.scrollIntoView({ block: 'center' });
    });
  if (document.readyState === 'complete') place();
  else addEventListener('load', place, { once: true });
}
