// node --test (Node 24는 .ts를 그대로 실행)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { exifTakenAt, fitSize, mp4CreatedAt, photoTakenAt, stripJpeg } from '../src/lib/exif.ts';

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
test('이상한 EXIF(포인터 개수 5)는 예외 없이 null', () => {
  const buf = new Uint8Array(jpeg('2026:10:21 15:30:00'));
  // IFD0의 0x8769 항목 개수를 5로(값이 포인터로 해석돼 범위 밖을 가리킴)
  buf[6 + 6 + 8 + 2 + 4] = 5;
  assert.equal(exifTakenAt(buf.buffer), null);
});
test('긴 변 맞추기', () => {
  assert.deepEqual(fitSize(4032, 3024, 2048), { width: 2048, height: 1536 });
  assert.deepEqual(fitSize(800, 600, 2048), { width: 800, height: 600 });
  assert.deepEqual(fitSize(1000, 4000, 480), { width: 120, height: 480 });
});

// ---- HEIC·PNG·영상(87) ----
const u32 = (n: number) => [n >>> 24, (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff];
const u16 = (n: number) => [n >> 8, n & 0xff];
const cc = (t: string) => [...t].map((c) => c.charCodeAt(0));
const box = (type: string, body: number[]) => [...u32(8 + body.length), ...cc(type), ...body];
/** jpeg()에서 TIFF 부분만(FFD8 FFE1 길이 'Exif\0\0' 12바이트 뒤, 끝 FFD9 앞) */
const tiffOf = (date: string, offset?: string) => [...new Uint8Array(jpeg(date, { offset }))].slice(12, -2);

/** 최소 HEIC: ftyp + meta(iinf: 1 hvc1, 2 Exif / iloc) + mdat 또는 meta 안 idat */
function heic(date: string, opts: { idat?: boolean; noExif?: boolean } = {}): Uint8Array<ArrayBuffer> {
  const exif = [...u32(6), ...cc('Exif'), 0, 0, ...tiffOf(date)];
  const infe = (id: number, type: string) => box('infe', [2, 0, 0, 0, ...u16(id), ...u16(0), ...cc(type), 0]);
  const iinf = box('iinf', [0, 0, 0, 0, ...u16(2), ...infe(1, 'hvc1'), ...infe(2, opts.noExif ? 'mime' : 'Exif')]);
  const ver = opts.idat ? 1 : 0;
  const iloc = (off: number) => box('iloc', [ver, 0, 0, 0, 0x44, 0x00, ...u16(1), ...u16(2), ...(ver ? u16(1) : []), ...u16(0), ...u16(1), ...u32(off), ...u32(exif.length)]);
  const ftyp = box('ftyp', [...cc('heic'), 0, 0, 0, 0, ...cc('mif1'), ...cc('heic')]);
  const meta = (off: number) => box('meta', [0, 0, 0, 0, ...box('hdlr', [0, 0, 0, 0, 0, 0, 0, 0, ...cc('pict'), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), ...iinf, ...iloc(off), ...(opts.idat ? box('idat', exif) : [])]);
  if (opts.idat) return new Uint8Array([...ftyp, ...meta(0)]);
  const head = ftyp.length + meta(0).length;
  return new Uint8Array([...ftyp, ...meta(head + 8), ...box('mdat', exif), ...new Array(100).fill(7)]);
}
test('HEIC: mdat 안 Exif 항목', async () => {
  assert.equal(await photoTakenAt(new Blob([heic('2026:10:21 15:30:00')])), '2026-10-21T06:30:00.000Z');
});
test('HEIC: meta 안 idat의 Exif 항목(iloc 방식 1)', async () => {
  assert.equal(await photoTakenAt(new Blob([heic('2025:01:02 03:04:05', { idat: true })])), '2025-01-01T18:04:05.000Z');
});
test('HEIC: Exif 항목 없음·잘림은 null', async () => {
  assert.equal(await photoTakenAt(new Blob([heic('2026:10:21 15:30:00', { noExif: true })])), null);
  assert.equal(await photoTakenAt(new Blob([heic('2026:10:21 15:30:00').slice(0, 60)])), null);
});
test('PNG eXIf', async () => {
  const sig = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  const chunk = (t: string, d: number[]) => [...u32(d.length), ...cc(t), ...d, 0, 0, 0, 0];
  const png = (withExif: boolean) => new Blob([new Uint8Array([...sig, ...chunk('IHDR', new Array(13).fill(0)), ...(withExif ? chunk('eXIf', tiffOf('2026:10:21 15:30:00', '+00:00')) : []), ...chunk('IDAT', [1, 2]), ...chunk('IEND', [])])]);
  assert.equal(await photoTakenAt(png(true)), '2026-10-21T15:30:00.000Z');
  assert.equal(await photoTakenAt(png(false)), null);
});
test('믿을 수 없는 사진 시각(1980년·미래)은 null', async () => {
  assert.equal(await photoTakenAt(new Blob([jpeg('1980:01:01 00:00:00')])), null);
  assert.equal(await photoTakenAt(new Blob([jpeg('2099:01:01 00:00:00')])), null);
  assert.equal(await photoTakenAt(new Blob([heic('1980:01:01 00:00:00')])), null);
});
test('JPEG은 종류 표시 없이도(바이트로 판별)', async () => {
  assert.equal(await photoTakenAt(new Blob([jpeg('2026:10:21 15:30:00')])), '2026-10-21T06:30:00.000Z');
});

/** 최소 MP4: ftyp + (mdat, moov 순서 고를 수 있음). mvhd 만든 시각은 1904년부터 초 */
function mp4(unix: number, opts: { v1?: boolean; moovFirst?: boolean } = {}): Blob {
  const secs = unix + 2082844800;
  const mvhd = opts.v1
    ? box('mvhd', [1, 0, 0, 0, ...u32(Math.floor(secs / 2 ** 32)), ...u32(secs >>> 0), ...new Array(8 + 4 + 8 + 80).fill(0)])
    : box('mvhd', [0, 0, 0, 0, ...u32(secs), ...new Array(4 + 4 + 4 + 80).fill(0)]);
  const moov = box('moov', [...mvhd, ...box('trak', [])]);
  const mdat = box('mdat', new Array(5000).fill(1));
  const ftyp = box('ftyp', [...cc('isom'), 0, 0, 2, 0]);
  return new Blob([new Uint8Array(opts.moovFirst ? [...ftyp, ...moov, ...mdat] : [...ftyp, ...mdat, ...moov])]);
}
test('MP4 mvhd 만든 시각(moov 끝·앞, 버전 0·1)', async () => {
  const t = Date.UTC(2026, 9, 21, 6, 30) / 1000;
  assert.equal(await mp4CreatedAt(mp4(t)), '2026-10-21T06:30:00.000Z');
  assert.equal(await mp4CreatedAt(mp4(t, { moovFirst: true })), '2026-10-21T06:30:00.000Z');
  assert.equal(await mp4CreatedAt(mp4(t, { v1: true })), '2026-10-21T06:30:00.000Z');
});
test('MP4 만든 시각이 0(1904년)·미래·moov 없음은 null', async () => {
  assert.equal(await mp4CreatedAt(mp4(-2082844800)), null);
  assert.equal(await mp4CreatedAt(mp4(Math.floor(Date.now() / 1000) + 9 * 3600)), null); // 현지 시각을 UTC로 적은 갓 찍은 영상
  assert.equal(await mp4CreatedAt(new Blob([new Uint8Array(box('ftyp', cc('isom')))])), null);
});

/** 표지(marker)와 내용으로 JPEG 조각 */
const seg = (m: number, body: number[]) => [0xff, m, (body.length + 2) >> 8, (body.length + 2) & 0xff, ...body];
const ascii = (s: string) => [...s].map((c) => c.charCodeAt(0));
/** Orientation 하나만 든 EXIF(리틀 엔디언) */
const orient = (o: number) => seg(0xe1, [...ascii('Exif'), 0, 0, 0x49, 0x49, 42, 0, 8, 0, 0, 0, 1, 0, 0x12, 0x01, 3, 0, 1, 0, 0, 0, o, 0, 0, 0, 0, 0, 0, 0]);
const pic = [...seg(0xdb, [0, 1, 2]), ...seg(0xc0, [8, 0, 1, 0, 1, 1]), ...seg(0xda, [1, 1, 0]), 0x12, 0xff, 0x00, 0x34, 0xff, 0xd0, 0x56, 0xff, 0xd9];
const buf = (...parts: number[][]) => new Uint8Array([0xff, 0xd8, ...parts.flat()]).buffer;

test('stripJpeg: EXIF·XMP·주석·끝 데이터는 빼고 JFIF·ICC·Adobe·그림은 그대로', () => {
  const jfif = seg(0xe0, [...ascii('JFIF'), 0, 1, 1]);
  const icc = seg(0xe2, [...ascii('ICC_PROFILE'), 0, 1, 1, 9]);
  const mpf = seg(0xe2, [...ascii('MPF'), 0, 1]);
  const adobe = seg(0xee, [...ascii('Adobe'), 1]);
  const xmp = seg(0xe1, [...ascii('http://ns.adobe.com/xap/1.0/'), 0]);
  const out = stripJpeg(buf(jfif, orient(1), xmp, icc, mpf, seg(0xfe, ascii('hi')), adobe, pic, [0xff, 0xd8, 9, 9]));
  assert.deepEqual(out, new Uint8Array([0xff, 0xd8, ...jfif, ...icc, ...adobe, ...pic]));
  // EXIF가 아예 없어도 된다
  assert.deepEqual(stripJpeg(buf(pic)), new Uint8Array([0xff, 0xd8, ...pic]));
});
test('stripJpeg: 회전 정보가 있거나 깨졌으면 null', () => {
  assert.equal(stripJpeg(buf(orient(6), pic)), null);
  assert.equal(stripJpeg(buf(orient(3), pic)), null);
  assert.equal(stripJpeg(buf(pic.slice(0, -2))), null); // EOI 없음
  assert.equal(stripJpeg(buf([0xff, 0xdb, 0, 40, 1])), null); // 길이가 파일 밖
  assert.equal(stripJpeg(new Uint8Array([0x89, 0x50, 0x4e, 0x47]).buffer), null);
});
test('stripJpeg: 프로그레시브 스캔 사이의 EXIF·주석도 빼고, 사이 표 안의 FF D9에서 자르지 않음', () => {
  const scan = (d: number[]) => [...seg(0xda, [1, 1, 0]), ...d];
  const dht = seg(0xc4, [0x10, 0xff, 0xd9, 1]); // 표 안에 우연히 FF D9
  const out = stripJpeg(buf(seg(0xc2, [8, 0, 1, 0, 1, 1]), scan([0x11, 0xff, 0x00]), orient(1), seg(0xfe, ascii('x')), dht, scan([0x22, 0xff, 0xd3, 0x33]), [0xff, 0xd9]));
  assert.deepEqual(out, new Uint8Array([0xff, 0xd8, ...seg(0xc2, [8, 0, 1, 0, 1, 1]), ...scan([0x11, 0xff, 0x00]), ...dht, ...scan([0x22, 0xff, 0xd3, 0x33]), 0xff, 0xd9]));
});
test('stripJpeg: 그림 데이터 밖의 길이 없는 표지는 null', () => {
  assert.equal(stripJpeg(buf([0xff, 0x01], pic)), null);
  assert.equal(stripJpeg(buf([0xff, 0xd0], pic)), null);
});
