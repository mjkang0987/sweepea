// 결과별 안내 문구. 부모 둘 다에게 해당하는 말은 "엄마아빠"(디자인 시스템 호칭 규칙)
export const NOTICES = {
  not_found: { title: '가족에게 받은 주소로 들어와 주세요', text: '카톡이나 문자로 받은 주소를 누르면 사진이 열려요.' },
  expired: { title: '주소 기간이 지났어요', text: '이 주소로는 이제 새로 들어올 수 없어요. 엄마아빠에게 새 주소를 받아 주세요.' },
  closed: { title: '앨범이 닫혔어요', text: '엄마아빠가 앨범을 닫았어요. 궁금한 게 있으면 엄마아빠에게 물어봐 주세요.' },
  revoked: { title: '이 휴대폰으로는 볼 수 없어요', text: '엄마아빠가 이 휴대폰을 가족 목록에서 뺐어요. 엄마아빠에게 물어봐 주세요.' },
  pending_expired: { title: '확인 기간이 지났어요', text: '3일 동안 엄마아빠 확인이 없어서 들어가기가 취소됐어요. 엄마아빠에게 사진 주소를 다시 받아 주세요.' },
} as const;

export type NoticeKey = keyof typeof NOTICES;
