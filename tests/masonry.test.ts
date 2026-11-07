import { test } from 'node:test';
import assert from 'node:assert/strict';
import { masonry, ratioOf } from '../src/lib/masonry.ts';

test('가장 짧은 줄에 차례로 쌓는다', () => {
  // 세로 긴 사진, 가로 사진, 가로 사진 → 두 번째는 오른쪽, 세 번째는 오른쪽(왼쪽이 더 길어서)
  assert.deepEqual(masonry([1.5, 0.75, 0.75], 2), [
    { col: 1, row: 1, span: 61 },
    { col: 2, row: 1, span: 31 },
    { col: 2, row: 32, span: 31 },
  ]);
  // 같으면 왼쪽부터
  assert.deepEqual(masonry([1, 1], 2).map((x) => x.col), [1, 2]);
});

test('비율: 모르면 정사각, 너무 길거나 납작하면 자름', () => {
  assert.equal(ratioOf(null, null), 1);
  assert.equal(ratioOf(4000, 3000), 0.75);
  assert.equal(ratioOf(1000, 5000), 1.6);
  assert.equal(ratioOf(5000, 1000), 0.6);
});
