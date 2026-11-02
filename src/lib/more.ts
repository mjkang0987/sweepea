// 목록 화면 공통(브라우저): 아래로 내리면 다음 쪽 이어 붙이기, 크게 보기에서 닫고 돌아오면 보던 자리로
import { masonry } from './masonry';

/** 엇갈린 배열 다시 계산(넓은 화면 자리: 가족 4줄 --c4, 엄빠 5줄 --c5)(같은 묶음이 쪽을 넘어 이어져 칸을 합친 뒤 그 묶음 전체로). 앞에서부터 쌓으므로 이미 있던 칸 자리는 그대로 */
export function relayout(ul: HTMLElement) {
  const cells = [...ul.children] as HTMLElement[];
  const r = cells.map((c) => Number(c.dataset.ratio) || 1);
  const two = masonry(r, 2);
  const four = masonry(r, 4);
  const five = masonry(r, 5);
  cells.forEach((c, i) => {
    for (const [k, v] of Object.entries({ c2: two[i].col, r2: two[i].row, s2: two[i].span, c4: four[i].col, r4: four[i].row, s4: four[i].span, c5: five[i].col, r5: five[i].row, s5: five[i].span })) c.style.setProperty(`--${k}`, String(v));
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

/** 넘겨 보기(옆으로 넘기는 줄, 가족·엄빠 공용): 옆으로 밀다 남은 카드가 다섯 장쯤이면 다음 쪽 카드(.sp-a__slide)를 뒤에 붙인다 */
export function swipeMore(swipe: HTMLElement) {
  const more = autoMore((doc) => [...doc.querySelectorAll<HTMLElement>('.sp-a__slide')].map((li) => swipe.appendChild(document.importNode(li, true))), { observe: false });
  const near = () => {
    if (swipe.scrollLeft + swipe.clientWidth * 6 >= swipe.scrollWidth) more();
  };
  swipe.addEventListener('scroll', near, { passive: true });
  near();
}

/** 앞으로(최근 쪽) 이어 붙이기(128·129): 사진 주변만 그린 앨범(닫고 돌아옴·달 카드)의 [data-less] '최근 사진 더 보기' 쪽을 받아 목록 앞에 붙인다.
 * 칸(세로): 링크가 화면 600px 안에 오면 받고, 보던 칸이 안 움직이게 세로 스크롤 보정, 그 달 표식(anchor)은 더 최근 칸으로 옮김.
 * 넘겨 보기(옆): 앞쪽 끝에서 카드 여섯 장쯤 남으면 받고 가로 스크롤 보정(보던 카드 그대로). 이미 있는 사진(맨 위 '방금 올라왔어요')은 건너뜀.
 * 못 받으면 다시 저절로 받지 않는다(누르면 그 쪽 페이지로) */
export function lessMore(o: { list: () => HTMLElement | null; items: string; anchor?: string; swipe?: boolean; after?: (ul: HTMLElement) => void }) {
  let busy = false;
  let failed = false;
  const load = async () => {
    const el = document.querySelector<HTMLElement>('[data-less]');
    const a = el?.querySelector('a');
    const ul = o.list();
    if (!el || !a || !ul || busy || failed) return;
    busy = true;
    try {
      const res = await fetch(a.href, { credentials: 'same-origin' });
      if (!res.ok || (res.redirected && new URL(res.url).pathname !== new URL(a.href).pathname)) throw new Error(String(res.status));
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      const ref = o.swipe ? undefined : ([...ul.children] as HTMLElement[]).find((c) => c.getBoundingClientRect().bottom > 0);
      const top0 = ref?.getBoundingClientRect().top ?? 0;
      const w0 = ul.scrollWidth;
      const left0 = ul.scrollLeft;
      const frag = document.createDocumentFragment();
      for (const li of doc.querySelectorAll<HTMLElement>(o.items)) {
        if (li.id && document.getElementById(li.id)) continue;
        const mark = o.anchor ? li.querySelector<HTMLElement>(o.anchor) : null;
        if (mark) document.getElementById(mark.id)?.remove();
        frag.appendChild(document.importNode(li, true));
      }
      ul.insertBefore(frag, ul.firstChild);
      o.after?.(ul);
      if (o.swipe) ul.scrollLeft = left0 + (ul.scrollWidth - w0);
      else if (ref) scrollBy(0, ref.getBoundingClientRect().top - top0);
      const next = doc.querySelector<HTMLElement>('[data-less]');
      if (next) {
        const n = document.importNode(next, true);
        n.hidden = !!o.swipe;
        el.replaceWith(n);
      } else el.remove();
    } catch {
      failed = true;
    } finally {
      busy = false;
    }
    watch();
  };
  let io: IntersectionObserver | null = null;
  const watch = () => {
    if (o.swipe) {
      const ul = o.list();
      if (ul && ul.scrollLeft < ul.clientWidth * 6) void load();
      return;
    }
    const el = document.querySelector<HTMLElement>('[data-less]');
    if (!el || typeof IntersectionObserver !== 'function') return;
    io?.disconnect();
    io = new IntersectionObserver((es) => es.some((e) => e.isIntersecting) && (io?.disconnect(), void load()), { rootMargin: '600px 0px' });
    io.observe(el);
  };
  // 넘겨 보기는 앞으로 밀면(손가락·키보드 모두 옆 스크롤) 저절로 붙으니 버튼은 스크립트 없을 때만(카드를 아래로 밀어내지 않게)
  if (o.swipe) {
    const el = document.querySelector<HTMLElement>('[data-less]');
    if (el) el.hidden = true;
  }
  // 닫고 돌아와 그 사진으로 옮긴 뒤부터 지켜본다(처음 그릴 때 맨 앞이라 바로 받아 버리지 않게)
  const start = () =>
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        if (!document.querySelector('[data-less]')) return;
        if (o.swipe) o.list()?.addEventListener('scroll', watch, { passive: true });
        watch();
      }),
    );
  if (document.readyState === 'complete') start();
  else addEventListener('load', start, { once: true });
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

const CLOSE = 'sp-close';
const SEEN = 'sp-seen';

/** 크게 보기에서 '봤음'을 남긴 사진(사용자 2026-11-02 "신규 사진 확인하고 닫기 누르면 신규 배지 안 없어짐").
 * 닫기(뒤로 가기)로 돌아온 앨범을 사파리가 메모리에서 그대로 꺼내면(bfcache) 서버는 봤음을 알아도 화면엔 배지가 남아서, 앨범이 이 목록으로 빼 준다 */
export function noteSeen(id: string) {
  try {
    const s: string[] = JSON.parse(sessionStorage.getItem(SEEN) ?? '[]');
    if (!s.includes(id)) sessionStorage.setItem(SEEN, JSON.stringify([...s, id].slice(-200)));
  } catch {
    // 못 적으면 다음에 앨범을 새로 받을 때 빠진다
  }
}

/** '봤음' 남기기(가족 = 보신 기록, 엄빠 = parent): 남겼으면 돌아갈 앨범의 신규 배지도 빠지게(noteSeen) 하고 true. 못 남기면 false(134: 세 곳에 복사돼 있던 것) */
export async function postViews(id: string, parent = false): Promise<boolean> {
  try {
    const r = await fetch('/api/views', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ ids: [id], parent }), keepalive: true, credentials: 'same-origin' });
    if (r.ok) noteSeen(id);
    return r.ok;
  } catch {
    return false;
  }
}

/** 본 사진 칸의 '신규' 알약과 읽어 주는 글의 '신규, '를 뺀다(기념일 알약은 그대로) */
function dropSeen() {
  let seen: string[] = [];
  try {
    seen = JSON.parse(sessionStorage.getItem(SEEN) ?? '[]');
    sessionStorage.removeItem(SEEN);
  } catch {
    return;
  }
  for (const id of seen) {
    const el = document.getElementById(`c-${id}`) ?? document.getElementById(`p-${id}`);
    if (!el) continue;
    el.querySelectorAll('.sp-a__new:not(.sp-a__new--event), .sp-p__new:not(.sp-p__cell-mark)').forEach((x) => x.remove());
    el.querySelectorAll('.sp-a__pills, .sp-p__pills').forEach((x) => x.childElementCount || x.remove());
    el.querySelectorAll('[aria-label^="신규, "], [alt^="신규, "]').forEach((x) => {
      for (const at of ['aria-label', 'alt']) {
        const t = x.getAttribute(at);
        if (t?.startsWith('신규, ')) x.setAttribute(at, t.slice('신규, '.length));
      }
    });
  }
}
/** 크게 보기 '닫기'가 뒤로 가기로 돌아왔을 때(사용자 2026-11-01 "닫기 속도"): 브라우저가 들고 있던 앨범을 그대로 보여 주고
 * 마지막에 본 사진 칸(모아 보기 #c-, 넘겨 보기 #p-·#c-)으로 옮긴다. 그 칸이 이 앨범에 없으면 그 칸까지 그린 앨범(닫기 주소)을 새로 연다 */
export function closeReturn() {
  // 사진 칸·카드를 누르면 그 사진 id를 적어 둔다(크게 보기가 '앨범에서 왔음'을 안다)
  document.addEventListener('click', (e) => {
    const a = (e.target as Element).closest<HTMLAnchorElement>('a[href]');
    const m = a && /^\/(album|view)\/([0-9a-f-]{36})$/.exec(new URL(a.href, location.href).pathname);
    try {
      if (m) sessionStorage.setItem('sp-open', m[2]);
    } catch {
      // 못 적으면 닫기는 지금처럼 주소로
    }
  });
  addEventListener('pageshow', () => {
    dropSeen();
    let c: { id?: string; href?: string } | null = null;
    try {
      c = JSON.parse(sessionStorage.getItem(CLOSE) ?? 'null');
      sessionStorage.removeItem(CLOSE);
    } catch {
      c = null;
    }
    if (!c?.id) return;
    const el = document.getElementById(`c-${c.id}`) ?? document.getElementById(`p-${c.id}`);
    if (!el) return void (c.href && location.replace(c.href));
    el.scrollIntoView(el.classList.contains('sp-a__slide') ? { block: 'nearest', inline: 'center' } : { block: 'center' });
  });
}

