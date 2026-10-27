// 반응 이모지: 기기 기본 이모지(사용자 2026-10-27 "도트 느낌 말고 기본 이모지로"). 장식이라 aria-hidden으로 넣는다
import type { ReactionKind } from './backend';

export const EMOJI: Record<ReactionKind, { label: string; anim: string; char: string }> = {
  heart: { label: '하트', anim: 'beat', char: '❤️' },
  best: { label: '최고', anim: 'nod', char: '👍' },
  good: { label: '좋아', anim: 'bob', char: '😊' },
  moved: { label: '감동', anim: 'wobble', char: '😭' },
  sparkle: { label: '반짝', anim: 'twinkle', char: '✨' },
};
