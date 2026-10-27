// 한마디 보낸 결과(주소 say=…)를 토스트 문구로. 보냄은 초록 하트, 나머지는 빨간 느낌표
export interface SayNote {
  text: string;
  tone: 'ok' | 'error';
}

export function sayNote(say: string | null | undefined, sentText = '보냈어요. 가족 모두 볼 수 있어요.'): SayNote | null {
  switch (say) {
    case 'sent':
      return { text: sentText, tone: 'ok' };
    case 'empty':
      return { text: '한마디를 써 주세요.', tone: 'error' };
    case 'limit':
      return { text: '오늘은 한마디를 많이 보냈어요. 내일 다시 보내 주세요.', tone: 'error' };
    case 'error':
      return { text: '보내지 못했어요. 잠시 뒤에 다시 보내 주세요.', tone: 'error' };
    default:
      return null;
  }
}
