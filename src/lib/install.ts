// 홈 화면에 두기 안내: 기기 종류(User-Agent)와 '다음에 할게요'·'알겠어요' 쿠키
export type InstallPlatform = 'inapp' | 'ios' | 'android' | 'other';

/** 앱 안 브라우저(카톡·네이버·라인·인스타·페이스북·밴드)는 홈 화면에 둘 수 없어 먼저 거른다(UA에 기기 이름이 같이 있다).
 *  단계를 아는 건 아이폰 사파리·안드로이드 크롬뿐: 다른 브라우저(아이폰 크롬·웨일, 삼성 인터넷)는 메뉴 위치가 달라 안내하지 않는다 */
export function installPlatform(ua: string): InstallPlatform {
  if (/KAKAOTALK|NAVER\(inapp|Line\/|Instagram|FBAN|FBAV|BAND\//i.test(ua)) return 'inapp';
  if (/iPhone|iPad|iPod/.test(ua)) return /CriOS|FxiOS|EdgiOS|Whale|NAVER/.test(ua) ? 'other' : 'ios';
  if (/Android/.test(ua)) return /SamsungBrowser|Whale|NAVER|Firefox/.test(ua) ? 'other' : 'android';
  return 'other';
}

export const INSTALL_COOKIE = 'sp_install';
/** 다음에 할게요: 7일 뒤 다시, 알겠어요: 1년 */
export const INSTALL_AGES = { later: 7 * 86_400, ok: 365 * 86_400 } as const;
