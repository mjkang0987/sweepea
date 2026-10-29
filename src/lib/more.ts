// 목록 화면 공통(브라우저): 아래로 내리면 다음 쪽 이어 붙이기, 크게 보기에서 닫고 돌아오면 보던 자리로
import { masonry } from './masonry';

/** 엇갈린 배열 다시 계산(같은 묶음이 쪽을 넘어 이어져 칸을 합친 뒤 그 묶음 전체로). 앞에서부터 쌓으므로 이미 있던 칸 자리는 그대로 */
export function relayout(ul: HTMLElement) {
  const cells = [...ul.children] as HTMLElement[];
  const r = cells.map((c) => Number(c.dataset.ratio) || 1);
  const two = masonry(r, 2);
  const four = masonry(r, 4);
  cells.forEach((c, i) => {
    for (const [k, v] of Object.entries({ c2: two[i].col, r2: two[i].row, s2: two[i].span, c4: four[i].col, r4: four[i].row, s4: four[i].span })) c.style.setProperty(`--${k}`, String(v));
  });
}

/** 목록 끝 [data-more] 안 '사진 더 보기' 링크가 화면에 가까워지면(600px 앞) 그 쪽을 받아 merge로 붙이고(붙인 칸들을 돌려줌), 받은 쪽의 끝 줄로 바꾼다.
 * 못 받으면 링크를 되돌려 둔다(누르면 그 쪽 페이지로). 돌려주는 함수는 지금 바로 받기(옆으로 넘기는 목록은 스스로 부른다, observe: false).
 * 화면 읽기에는 늘 있는 빈 알림 칸 하나로 알린다(내용이 든 채 새로 넣은 role=status는 대부분 읽지 않음). IntersectionObserver가 없으면 링크 그대로 */
export function autoMore(merge: (doc: Document) => HTMLElement[], { observe = true } = {}): () => void {
  const live = document.createElement('p');
  live.className = 'sp-vh';
  live.setAttribute('role', 'status');
  document.body.appendChild(live);
  const io = observe && typeof IntersectionObserver === 'function' ? new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && void load(e.target as HTMLElement)), { rootMargin: '600px 0px' }) : null;
  let busy = false;
  // 사진 크기를 그 자리에서 바꾸면 세대가 바뀐다: 그 전에 받기 시작한 쪽은 버린다(옛 단계 칸이 새 목록에 섞이지 않게, 리뷰 2026-10-29)
  let gen = 0;
  const watch = () => {
    const el = document.querySelector<HTMLElement>('[data-more]');
    if (io && el?.querySelector('a')) io.observe(el);
  };
  async function load(el: HTMLElement) {
    io?.unobserve(el);
    const a = el.querySelector('a');
    if (!a || busy) return;
    busy = true;
    // 키보드로 링크에 와 있었으면 붙인 첫 칸으로 초점을 옮긴다(링크가 사라져 초점이 맨 위로 떨어지지 않게)
    const focused = el.contains(document.activeElement);
    const wait = document.createElement('p');
    wait.className = 'sp-more__end';
    wait.innerHTML = '<img class="sp-more__kongi" src="/kongi.svg" width="32" height="32" alt="" />사진 불러오는 중…';
    el.replaceWith(wait);
    if (focused) wait.tabIndex = -1, wait.focus();
    live.textContent = '사진 불러오는 중';
    const mine = gen;
    try {
      const res = await fetch(a.href, { credentials: 'same-origin' });
      if (mine !== gen) return void (live.textContent = '');
      // 로그인이 풀리면 다른 화면으로 돌려보낸다
      if (res.redirected && new URL(res.url).pathname !== new URL(a.href).pathname) return void location.assign(res.url);
      if (!res.ok) throw new Error(String(res.status));
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      if (mine !== gen) return void (live.textContent = '');
      const added = merge(doc);
      const end = doc.querySelector('[data-more]');
      if (end) wait.replaceWith(document.importNode(end, true));
      else wait.remove();
      if (focused) added[0]?.querySelector<HTMLElement>('a')?.focus();
      live.textContent = end && !end.querySelector('a') ? `사진 ${added.length}장을 더 불러왔어요. 처음 사진까지 모두 봤어요` : `사진 ${added.length}장을 더 불러왔어요`;
      watch();
    } catch {
      if (mine !== gen) return void (live.textContent = '');
      // 다시 저절로 받지는 않는다(끝없이 되풀이하지 않게). 누르면 그 쪽 페이지로
      wait.replaceWith(el);
      el.dataset.failed = '';
      if (focused) el.querySelector('a')?.focus();
      live.textContent = '사진을 불러오지 못했어요. 사진 더 보기를 눌러 주세요';
    } finally {
      busy = false;
      // 세대가 바뀌어 버린 쪽이면, 그사이 새 목록 끝을 보던 감시가 busy라 그냥 끝났을 수 있어 다시 지켜본다(리뷰 2026-10-29)
      if (mine !== gen) watch();
    }
  }
  watch();
  // 사진 크기를 그 자리에서 바꾸면(zoomswap) 새 목록 끝을 다시 지켜본다
  document.addEventListener('sp:album-swapped', () => {
    gen++;
    watch();
  });
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
