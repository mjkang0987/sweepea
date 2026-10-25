// 매일 정리(예약 작업): 탈퇴 기한 지난 가족방 → 하루 지난 '올리는 중' 사진 → R2 정리 대기열의 폴더 파일 지우기.
// 백엔드·버킷을 받아서 돌린다(가짜로 단위 검사). 한 폴더가 실패해도 다음 폴더는 계속하고, 실패한 폴더는 대기열에 남아 내일 다시
import type { Backend } from '../lib/backend/types';

/** R2 버킷에서 쓰는 부분만 */
export interface CleanupBucket {
  list(o: { prefix: string; cursor?: string; limit?: number }): Promise<{ objects: { key: string }[]; truncated: boolean; cursor?: string }>;
  delete(keys: string[]): Promise<void>;
}

type CleanupBackend = Pick<Backend, 'purgeDeletedFamilies' | 'cleanupStaleUploads' | 'r2CleanupTake' | 'r2CleanupDone'>;

/** 접두사 아래 파일 모두 지우기(한 번에 1000개씩) */
export async function deletePrefix(bucket: CleanupBucket, prefix: string): Promise<number> {
  let n = 0;
  let cursor: string | undefined;
  do {
    const page = await bucket.list({ prefix, cursor, limit: 1000 });
    if (page.objects.length) await bucket.delete(page.objects.map((o) => o.key));
    n += page.objects.length;
    cursor = page.truncated ? page.cursor : undefined;
  } while (cursor);
  return n;
}

/** budget: 한 번에 쓸 외부 호출 수(Workers 무료는 요청당 50개). 폴더 하나에 최소 3번(목록·지우기·끝 표시)이라
 *  남은 호출이 모자라면 멈추고 나머지 폴더는 대기열에 남아 내일 이어서 한다 */
export async function runCleanup(backend: CleanupBackend, bucket: CleanupBucket, budget = 45) {
  let calls = 0;
  const errors: string[] = [];
  // 앞 단계가 실패해도 다음 단계는 한다(실패는 모아서 알린다)
  const step = async <T>(name: string, f: () => Promise<T>, fallback: T): Promise<T> => {
    calls++;
    try {
      return await f();
    } catch (e) {
      errors.push(`${name}: ${e instanceof Error ? e.message : String(e)}`);
      return fallback;
    }
  };
  const families = await step('가족방', () => backend.purgeDeletedFamilies(), [] as string[]);
  const stale = await step('올리는 중', () => backend.cleanupStaleUploads(), 0);
  let folders = 0;
  let files = 0;
  const failed: string[] = [];
  const take = Math.max(0, Math.floor((budget - calls - 1) / 3));
  const queue = take ? await step('대기열', () => backend.r2CleanupTake(take), [] as string[]) : [];
  for (const prefix of queue) {
    if (budget - calls < 3) break;
    // 대기열 값은 DB가 형식을 검사한다. 그래도 빈 접두사로 버킷 전체를 지우지 않게 한 번 더
    if (!/^[0-9a-f-]{36}\/([0-9a-f-]{36}\/)?$/.test(prefix)) {
      failed.push(prefix);
      errors.push(`이상한 접두사: ${prefix}`);
      continue;
    }
    try {
      const n = await deletePrefix(bucket, prefix);
      // 목록 쪽수만큼(+ 지우기) 호출을 쓴다
      calls += 2 * Math.max(1, Math.ceil(n / 1000));
      files += n;
      calls++;
      await backend.r2CleanupDone(prefix);
      folders++;
    } catch (e) {
      calls += 2;
      failed.push(prefix);
      errors.push(`R2 ${prefix}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }
  return { families: families.length, stale, folders, files, failed, errors, calls };
}
