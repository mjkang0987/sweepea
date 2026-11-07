// 가족방 목록(sp_me)에서 화면이 쓰는 분류
import type { EntryMe } from './backend';

export const isOpen = (f: EntryMe & { closed?: boolean }) => f.device === 'active' && f.member === 'active' && !f.closed;
export const isWaiting = (f: EntryMe & { closed?: boolean }) =>
  !f.closed && f.device !== 'revoked' && (f.device === 'pending' || f.member === 'pending');
