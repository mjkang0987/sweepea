// node --test (Node 24는 .ts를 그대로 실행)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { exifTakenAt, fitSize } from '../src/lib/exif.ts';

/** EXIF가 든 최소 JPEG(빅/리틀 엔디언, 시간대 있음/없음) */
function jpeg(date: string, opts: { le?: boolean; offset?: string } = {}): ArrayBuffer {
  const le = opts.le ?? true;
  const tiff: number[] = [];
  const w16 = (n: number) => (le ? tiff.push(n & 0xff, n >> 8) : tiff.push(n >> 8, n & 0xff));
  const w32 = (n: number) => (le ? tiff.push(n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, n >>> 24) : tiff.push(n >>> 24, (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff));
  const tags = opts.offset ? 2 : 1;
  // 헤더(8) + IFD0(2+12+4=18) → Exif IFD at 26: 2 + 12*tags + 4, 그 뒤 값
  const exifIfd = 26;
  const values = exifIfd + 2 + 12 * tags + 4;
  le ? tiff.push(0x49, 0x49) : tiff.push(0x4d, 0x4d);
  w16(42);
  w32(8);
  w16(1);
  w16(0x8769); w16(4); w32(1); w32(exifIfd);
  w32(0);
  w16(tags);
  w16(0x9003); w16(2); w32(20); w32(values);
  if (opts.offset) {
    w16(0x9011); w16(2); w32(7); w32(values + 20);
  }
  w32(0);
  for (const c of date + '\0') tiff.push(c.charCodeAt(0));
  if (opts.offset) for (const c of opts.offset + '\0') tiff.push(c.charCodeAt(0));
  const app1 = [0x45, 0x78, 0x69, 0x66, 0, 0, ...tiff];
  const len = app1.length + 2;
  return new Uint8Array([0xff, 0xd8, 0xff, 0xe1, len >> 8, len & 0xff, ...app1, 0xff, 0xd9]).buffer;
}

test('EXIF 촬영 시각(시간대 없으면 한국 시간)', () => {
  assert.equal(exifTakenAt(jpeg('2026:10:21 15:30:00')), '2026-10-21T06:30:00.000Z');
});
test('빅 엔디언 + 시간대', () => {
  assert.equal(exifTakenAt(jpeg('2026:10:21 15:30:00', { le: false, offset: '+00:00' })), '2026-10-21T15:30:00.000Z');
});
test('EXIF 없음·JPEG 아님·빈 날짜', () => {
  assert.equal(exifTakenAt(new Uint8Array([0xff, 0xd8, 0xff, 0xda, 0, 2]).buffer), null);
  assert.equal(exifTakenAt(new Uint8Array([0x89, 0x50, 0x4e, 0x47]).buffer), null);
  assert.equal(exifTakenAt(jpeg('0000:00:00 00:00:00')), null);
  assert.equal(exifTakenAt(jpeg('2026:10:21 15:30:00').slice(0, 30)), null);
});
test('긴 변 맞추기', () => {
  assert.deepEqual(fitSize(4032, 3024, 2048), { width: 2048, height: 1536 });
  assert.deepEqual(fitSize(800, 600, 2048), { width: 800, height: 600 });
  assert.deepEqual(fitSize(1000, 4000, 480), { width: 120, height: 480 });
});
