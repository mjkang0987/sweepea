// 링크 카드의 '주소 복사'(data-copy="입력칸 id"). 아이폰 사파리는 읽기 전용 칸을 길게 눌러도 복사 메뉴가 안 떠서 버튼으로.
// 버튼은 스크립트가 있을 때만 보이게(hidden을 풂). 카드가 그 자리에서 바뀌어도 되게 문서에서 받는다

/** root 안의 복사 버튼을 보이게 */
export const revealCopy = (root: Pick<Element, 'querySelectorAll'>) => root.querySelectorAll<HTMLElement>('[data-copy]').forEach((b) => (b.hidden = false));

/** 복사 버튼 누르기를 한 번만 걸어 둔다. 결과는 say로 알린다. 못 하면 칸을 골라 두어 휴대폰 복사 메뉴로 */
export function wireCopy(say: (text: string) => void) {
  revealCopy(document);
  document.addEventListener('click', (e) => {
    const b = (e.target as Element).closest<HTMLElement>('[data-copy]');
    const input = b && document.getElementById(b.dataset.copy!);
    if (!(input instanceof HTMLInputElement)) return;
    const pick = () => {
      input.removeAttribute('readonly');
      input.focus();
      input.select();
      say('주소를 골라 두었어요. 복사를 눌러 주세요.');
    };
    if (navigator.clipboard) navigator.clipboard.writeText(input.value).then(() => say('주소를 복사했어요.'), pick);
    else pick();
  });
}
