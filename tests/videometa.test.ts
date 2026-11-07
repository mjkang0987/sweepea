import { test } from 'node:test';
import assert from 'node:assert/strict';
import { stripVideoLocation } from '../src/lib/videometa.ts';

const enc = new TextEncoder();
const u32 = (n: number) => new Uint8Array([n >>> 24, (n >>> 16) & 255, (n >>> 8) & 255, n & 255]);
const cat = (...xs: Uint8Array[]) => {
  const out = new Uint8Array(xs.reduce((a, x) => a + x.length, 0));
  let o = 0;
  for (const x of xs) (out.set(x, o), (o += x.length));
  return out;
};
const box = (type: string | Uint8Array, ...body: Uint8Array[]) => {
  const b = cat(...body);
  return cat(u32(b.length + 8), typeof type === 'string' ? enc.encode(type) : type, b);
};
const LOC = '+37.5665+126.9780+050.000/';
// 아이폰처럼: moov/udta/©xyz, moov/meta(hdlr·keys·ilst)에 위치·기종
const keyEntry = (name: string) => cat(u32(8 + name.length), enc.encode('mdta'), enc.encode(name));
const dataBox = (s: string) => box('data', u32(1), u32(0), enc.encode(s));
const moov = box(
  'moov',
  box('mvhd', new Uint8Array(20)),
  box('udta', box(new Uint8Array([0xa9, 0x78, 0x79, 0x7a]), new Uint8Array([0, 26, 0x15, 0xc7]), enc.encode(LOC)), box('loci', u32(0), enc.encode('LOCI-BINARY'))),
  box(
    'meta',
    box('hdlr', new Uint8Array(24)),
    box('keys', u32(0), u32(2), keyEntry('com.apple.quicktime.location.ISO6709'), keyEntry('com.apple.quicktime.make')),
    box('ilst', box(u32(1), dataBox(LOC)), box(u32(2), dataBox('Apple'))),
  ),
);
const file = cat(box('ftyp', enc.encode('qt  ')), box('mdat', enc.encode('VIDEO-DATA')), moov);
const text = (b: Uint8Array) => new TextDecoder('latin1').decode(b);

test('아이폰 영상 위치(©xyz·mdta location)를 지우고 크기·나머지는 그대로(138)', async () => {
  const out = new Uint8Array(await (await stripVideoLocation(new Blob([file], { type: 'video/quicktime' }))).arrayBuffer());
  assert.equal(out.length, file.length);
  assert.ok(!text(out).includes(LOC), '위치 글자가 남지 않음');
  assert.ok(!text(out).includes('location'), '위치 키 이름도 지움');
  assert.ok(!text(out).includes('LOCI-BINARY') && !text(out).includes('loci'), '3GPP loci(숫자 위치)도 지움');
  assert.ok(text(out).includes('Apple') && text(out).includes('com.apple.quicktime.make'), '다른 태그는 그대로');
  assert.ok(text(out).includes('VIDEO-DATA') && text(out).includes('ftyp'), '영상 데이터·앞부분 그대로');
  assert.ok(text(out).includes('free'), '지운 자리는 free 상자');
});

test('위치가 없거나 mp4가 아니면 받은 그대로', async () => {
  const plain = cat(box('ftyp', enc.encode('isom')), box('moov', box('mvhd', new Uint8Array(20))), box('mdat', enc.encode('x')));
  const b = new Blob([plain]);
  assert.equal(await stripVideoLocation(b), b);
  const junk = new Blob([enc.encode('not a video at all')]);
  assert.equal(await stripVideoLocation(junk), junk);
});
