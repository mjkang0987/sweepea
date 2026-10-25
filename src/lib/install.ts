// 홈 화면에 두기 안내: 기기 종류(User-Agent)와 '다음에 할게요'·'알겠어요' 쿠키
export type InstallPlatform = 'kakao' | 'ios' | 'android' | 'other';

/** 카톡 인앱 브라우저가 먼저(아이폰·안드로이드 둘 다 카톡 UA에 기기 이름이 같이 있다) */
export function installPlatform(ua: string): InstallPlatform {
  if (/KAKAOTALK/i.test(ua)) return 'kakao';
  if (/iPhone|iPad|iPod/.test(ua)) return 'ios';
  if (/Android/.test(ua)) return 'android';
  return 'other';
}

export const INSTALL_COOKIE = 'sp_install';
/** 다음에 할게요: 7일 뒤 다시, 알겠어요: 1년 */
export const INSTALL_AGES = { later: 7 * 86_400, ok: 365 * 86_400 } as const;
