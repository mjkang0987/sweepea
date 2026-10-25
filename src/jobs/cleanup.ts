// 매일 정리(예약 작업): 탈퇴 기한 지난 가족방 → 하루 지난 '올리는 중' 사진 → R2 정리 대기열의 폴더 파일 지우기.
// 백엔드·버킷을 받아서 돌린다(가짜로 단위 검사). 한 폴더가 실패해도 다음 폴더는 계속하고, 실패한 폴더는 대기열에 남아 내일 다시
import type { Backend } from '../lib/backend/types';

/** R2 버킷에서 쓰는 부분만 */
export interface CleanupBucket {
  list(o: { prefix: string; cursor?: string; limit?: number }): Promise<{ objects: { key: string }[]; truncated: boolean; cursor?: string }>;
  delete(keys: string[]): Promise<void>;
}

type CleanupBackend = Pick<Backend, 'purgeDeletedFamilies' | 'cleanupStaleUploads' | 'r2CleanupTake' | 'r2CleanupDone'>;

/** 남은 외부 호출 수. 쓰기 전에 하나씩 뺀다 */
export interface Budget {
  left: number;
}
const spend = (b: Budget) => {
  if (b.left <= 0) return false;
  b.left--;
  return true;
};

/** 접두사 아래 파일 지우기(한 번에 1000개씩). 호출이 모자라면 멈추고 false(다 지운 건 아님) */
export async function deletePrefix(bucket: CleanupBucket, prefix: string, budget: Budget = { left: Infinity }): Promise<{ files: number; complete: boolean }> {
  let files = 0;
  let cursor: string | undefined;
  do {
    if (!spend(budget)) return { files, complete: false };
    const page = await bucket.list({ prefix, cursor, limit: 1000 });
    if (page.objects.length) {
      if (!spend(budget)) return { files, complete: false };
      await bucket.delete(page.objects.map((o) => o.key));
    }
    files += page.objects.length;
    cursor = page.truncated ? page.cursor : undefined;
  } while (cursor);
  return { files, complete: true };
}

/** budget: 한 번에 쓸 외부 호출 수(Workers 무료는 요청당 50개). 다 쓰면 멈추고 남은 폴더는 대기열에 남아 내일 이어서 한다 */
export async function runCleanup(backend: CleanupBackend, bucket: CleanupBucket, limit = 45) {
  const budget: Budget = { left: limit };
  const errors: string[] = [];
  // 앞 단계가 실패해도 다음 단계는 한다(실패는 모아서 알린다)
  const step = async <T>(name: string, f: () => Promise<T>, fallback: T): Promise<T> => {
    if (!spend(budget)) return fallback;
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
  // 폴더 하나에 적어도 목록·지우기·끝 표시 3번
  const take = Math.floor((budget.left - 1) / 3);
  const queue = take > 0 ? await step('대기열', () => backend.r2CleanupTake(take), [] as string[]) : [];
  for (const prefix of queue) {
    if (budget.left < 3) break;
    // 대기열 값은 DB가 형식을 검사한다. 그래도 빈 접두사로 버킷 전체를 지우지 않게 한 번 더
    if (!/^[0-9a-f-]{36}\/([0-9a-f-]{36}\/)?$/.test(prefix)) {
      failed.push(prefix);
      errors.push(`이상한 접두사: ${prefix}`);
      continue;
    }
    try {
      const r = await deletePrefix(bucket, prefix, budget);
      files += r.files;
      // 다 못 지웠으면(호출이 모자람) 대기열에 그대로 두고 멈춘다
      if (!r.complete) break;
      if (!spend(budget)) break;
      await backend.r2CleanupDone(prefix);
      folders++;
    } catch (e) {
      failed.push(prefix);
      errors.push(`R2 ${prefix}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }
  return { families: families.length, stale, folders, files, failed, errors, calls: limit - budget.left };
}
