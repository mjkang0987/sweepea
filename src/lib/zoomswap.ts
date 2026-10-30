// 사진 크기 −/+를 페이지 전환 없이 그 자리에서(98e, 사용자 2026-10-29 "키우고 작아지는 거 페이지 전환이라 너무 구린데").
// 다음 단계 화면을 받아 사진 목록([data-album])과 바뀌는 부분만 갈아 끼우고, 화면에 보이던 칸은 View Transitions로 커지고 작아지며 자리를 옮긴다.
// 보던 사진은 화면 같은 높이에 그대로. 못 받으면 링크로 이동(지금과 같음). 움직임 줄이기면 애니메이션 없이 바로
const NAMED_MAX = 80;
const LABEL: Record<string, string> = { '1': '한 줄에 한 장', '2': '한 줄에 두 장', '3': '한 줄에 세 장', '5': '한 줄에 다섯 장', m: '달마다 대표 사진', y: '해마다 대표 사진' };

type Opts = {
  /** −/+ 링크 */
  button: string;
  /** 칸(id="c-<사진 id>") */
  cell: string;
  /** 위에 붙어 칸을 가리는 머리(보던 칸을 고를 때 그 아래부터) */
  head?: string;
  /** 사진 목록 말고 같이 바꿀 것(−/+ 묶음, 머리 작은 줄 등) */
  also: string[];
};

export function zoomInPlace({ button, cell, head, also }: Opts) {
  // 빈 알림 칸을 미리 둔다(내용이 든 채 새로 넣은 role=status는 대부분 읽지 않음). 이어 붙이기 알림 칸과 구분되게 data-zoom
  const live = document.createElement('p');
  live.className = 'sp-vh';
  live.setAttribute('role', 'status');
  live.dataset.zoom = '';
  document.body.appendChild(live);
  const say = (text: string) => (live.textContent = text);
  let busy = false;
  const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.addEventListener('click', (e) => {
    const a = (e.target as Element).closest<HTMLAnchorElement>(button);
    if (!a?.href || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    if (!busy) void go(a);
  });

  async function go(a: HTMLAnchorElement) {
    busy = true;
    const href = a.href;
    const which = [...document.querySelectorAll(button)].indexOf(a);
    try {
      const res = await fetch(href, { credentials: 'same-origin' });
      // 로그인이 풀리는 등 다른 화면이면 그리로
      if (res.redirected && new URL(res.url).pathname !== new URL(href).pathname) return void location.assign(res.url);
      if (!res.ok) throw new Error(String(res.status));
      const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
      const next = doc.querySelector('[data-album]');
      const now = document.querySelector('[data-album]');
      if (!next || !now) throw new Error('no album');

      // 보던 칸: 머리 아래 처음 보이는 칸과 그 높이. 화면에 보이는 칸들에 이름을 붙여 새 칸과 짝지음
      const top = head ? (document.querySelector(head)?.getBoundingClientRect().bottom ?? 0) : 0;
      const seen: HTMLElement[] = [];
      for (const li of document.querySelectorAll<HTMLElement>(cell)) {
        const r = li.getBoundingClientRect();
        if (r.bottom <= top) continue;
        if (r.top >= innerHeight || seen.length >= NAMED_MAX) break;
        seen.push(li);
      }
      const anchor = seen[0] ? { id: seen[0].id, y: seen[0].getBoundingClientRect().top } : null;
      const names = new Map(seen.map((li, i) => [li.id, `sp-z${i}`]));
      const animate = typeof document.startViewTransition === 'function' && !calm();
      if (animate) for (const li of seen) li.style.viewTransitionName = names.get(li.id)!;

      const apply = async () => {
        now.replaceWith(document.importNode(next, true));
        for (const sel of also) {
          const old = document.querySelector(sel), nw = doc.querySelector(sel);
          if (old && nw) old.replaceWith(document.importNode(nw, true));
        }
        history.replaceState(history.state, '', href);
        const same = anchor && document.getElementById(anchor.id);
        if (same) window.scrollBy(0, same.getBoundingClientRect().top - anchor.y);
        else window.scrollTo(0, 0);
        if (!animate) return;
        // 새 칸에 같은 이름, 그 칸 사진은 바로 그려 두고(늦으면 빈 칸으로 커짐) 잠깐만 기다린다
        const waits: Promise<unknown>[] = [];
        for (const [id, name] of names) {
          const li = document.getElementById(id);
          if (!li) continue;
          li.style.viewTransitionName = name;
          const img = li.querySelector('img');
          if (img) img.loading = 'eager', waits.push(img.decode().catch(() => undefined));
        }
        await Promise.race([Promise.all(waits), new Promise((r) => setTimeout(r, 300))]);
      };
      if (animate) {
        const t = document.startViewTransition(apply);
        // 갈아 끼우기가 실패하면 바깥에서 링크로 이동, 애니메이션만 실패하면 그대로
        await t.updateCallbackDone;
        await t.finished.catch(() => undefined);
        for (const id of names.keys()) document.getElementById(id)?.style.removeProperty('view-transition-name');
      } else await apply();

      // 누른 쪽 버튼에 초점(꺼졌으면 다른 쪽), 이어 붙이기는 새 목록 끝을 다시 지켜봄
      const btns = [...document.querySelectorAll<HTMLAnchorElement>(button)];
      if (a === document.activeElement || document.activeElement === document.body) (btns[which]?.href ? btns[which] : btns.find((b) => b.href))?.focus();
      document.dispatchEvent(new Event('sp:album-swapped'));
      say(LABEL[new URL(href).searchParams.get('z') ?? ''] ?? '사진 크기를 바꿨어요');
    } catch {
      location.assign(href);
    } finally {
      busy = false;
    }
  }
}
