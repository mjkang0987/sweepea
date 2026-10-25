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

export async function runCleanup(backend: CleanupBackend, bucket: CleanupBucket, batch = 200) {
  const families = await backend.purgeDeletedFamilies();
  const stale = await backend.cleanupStaleUploads();
  let folders = 0;
  let files = 0;
  const failed: string[] = [];
  for (const prefix of await backend.r2CleanupTake(batch)) {
    // 대기열 값은 DB가 형식을 검사한다. 그래도 빈 접두사로 버킷 전체를 지우지 않게 한 번 더
    if (!/^[0-9a-f-]{36}\/([0-9a-f-]{36}\/)?$/.test(prefix)) {
      failed.push(prefix);
      continue;
    }
    try {
      files += await deletePrefix(bucket, prefix);
      await backend.r2CleanupDone(prefix);
      folders++;
    } catch {
      failed.push(prefix);
    }
  }
  return { families: families.length, stale, folders, files, failed };
}
