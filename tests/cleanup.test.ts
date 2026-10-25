import { test } from 'node:test';
import assert from 'node:assert/strict';
import { runCleanup, type CleanupBucket } from '../src/jobs/cleanup.ts';

const F = '00000000-0000-4000-8000-00000000f001';
const M = '00000000-0000-4000-8000-0000000000a1';

function fakeBucket(keys: string[], failOn?: string): CleanupBucket & { keys: Set<string> } {
  const set = new Set(keys);
  return {
    keys: set,
    async list({ prefix, cursor, limit = 1000 }) {
      // R2처럼 커서는 '마지막으로 준 키 다음부터'(그 사이 지워도 건너뛰지 않는다)
      const all = [...set].filter((k) => k.startsWith(prefix) && (!cursor || k > cursor)).sort();
      const page = all.slice(0, limit);
      return { objects: page.map((key) => ({ key })), truncated: all.length > limit, cursor: page.at(-1) };
    },
    async delete(ks) {
      if (failOn && ks.some((k) => k.startsWith(failOn))) throw new Error('R2 오류');
      ks.forEach((k) => set.delete(k));
    },
  };
}

function fakeBackend(queue: string[]) {
  const done: string[] = [];
  return {
    done,
    purgeDeletedFamilies: async () => ['x'],
    cleanupStaleUploads: async () => 2,
    r2CleanupTake: async () => [...queue],
    r2CleanupDone: async (p: string) => void done.push(p),
  };
}

test('대기열 폴더의 파일을 지우고 끝 표시, 다른 폴더는 그대로', async () => {
  const other = '00000000-0000-4000-8000-00000000f002';
  const bucket = fakeBucket([`${F}/${M}/view-1`, `${F}/${M}/thumb-1`, `${F}/b/view-1`, `${other}/x/view-1`]);
  const backend = fakeBackend([`${F}/${M}/`]);
  const r = await runCleanup(backend, bucket);
  assert.deepEqual(r, { families: 1, stale: 2, folders: 1, files: 2, failed: [] });
  assert.deepEqual([...bucket.keys].sort(), [`${F}/b/view-1`, `${other}/x/view-1`]);
  assert.deepEqual(backend.done, [`${F}/${M}/`]);
});

test('가족방 폴더는 여러 쪽에 걸쳐도 다 지운다', async () => {
  const keys = Array.from({ length: 2500 }, (_, i) => `${F}/m${i}/view-${i}`);
  const bucket = fakeBucket(keys);
  const r = await runCleanup(fakeBackend([`${F}/`]), bucket);
  assert.equal(r.files, 2500);
  assert.equal(bucket.keys.size, 0);
});

test('실패한 폴더·이상한 접두사는 대기열에 남긴다', async () => {
  const bucket = fakeBucket([`${F}/${M}/view-1`]);
  const backend = fakeBackend([`${F}/${M}/`, '', '../']);
  const failing = fakeBucket([`${F}/${M}/view-1`], `${F}/${M}/`);
  const r = await runCleanup(backend, failing);
  assert.deepEqual(r.failed, [`${F}/${M}/`, '', '../']);
  assert.deepEqual(backend.done, []);
  assert.equal(failing.keys.size, 1);
  void bucket;
});
