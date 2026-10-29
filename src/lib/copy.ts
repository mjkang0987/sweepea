// 링크 카드의 '주소 복사'(data-copy="입력칸 id"). 아이폰 사파리는 읽기 전용 칸을 길게 눌러도 복사 메뉴가 안 떠서 버튼으로.
// 버튼은 스크립트가 있을 때만 보이게(hidden을 풂). 카드가 그 자리에서 바뀌어도 되게 문서에서 받는다

/** root 안의 복사 버튼을 보이게 */
export const revealCopy = (root: Pick<Element, 'querySelectorAll'>) => root.querySelectorAll<HTMLElement>('[data-copy]').forEach((b) => (b.hidden = false));

/** text를 복사하고 say로 알린다. 못 하면 주소 칸을 골라 두고 직접 복사하게 안내(칸은 벗어나면 다시 읽기 전용) */
export function copyText(input: HTMLInputElement, text: string, say: (text: string) => void, ok = '주소를 복사했어요.') {
  const pick = () => {
    input.readOnly = false;
    input.addEventListener('blur', () => (input.readOnly = true), { once: true });
    input.focus();
    input.select();
    say('주소만 골라 두었어요. 휴대폰은 칸을 길게 눌러 복사를, 컴퓨터는 Ctrl+C(맥은 ⌘C)를 눌러 주세요.');
  };
  if (navigator.clipboard) navigator.clipboard.writeText(text).then(() => say(ok), pick);
  else pick();
}

/** 복사 버튼 누르기를 한 번만 걸어 둔다 */
export function wireCopy(say: (text: string) => void) {
  revealCopy(document);
  document.addEventListener('click', (e) => {
    const b = e.target instanceof Element ? e.target.closest<HTMLElement>('[data-copy]') : null;
    const input = b && document.getElementById(b.dataset.copy!);
    if (input instanceof HTMLInputElement) copyText(input, input.value, say);
  });
}
