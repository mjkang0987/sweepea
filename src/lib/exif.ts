// 사진·영상 파일 안의 촬영 시각을 읽고, JPEG의 위치·기기 정보를 빼고, 위치를 뺀 사진 정보를 새 JPEG에 옮긴다(라이브러리 없이). JPEG·PNG는 앞부분(128KB 정도)이면 충분하고, HEIC은 Exif 항목 자리를 찾아 그 부분만 더 읽는다

const HEAD = 128 * 1024;

/** 사진 파일의 촬영 시각(ISO). 종류 표시가 아니라 앞부분 바이트로 JPEG·HEIC·PNG를 가린다. 없거나 깨졌으면 null
 * shortcut: WebP는 EXIF가 보통 파일 끝이라 안 읽음, 폰 사진이 WebP로 오기 시작하면 끝부분도 읽는다 */
export async function photoTakenAt(file: Blob): Promise<string | null> {
  const iso = await readPhoto(file);
  return iso && plausible(Date.parse(iso)) ? iso : null;
}

/** 파일 안 시각으로 믿을 만한가: 2001년부터 지금(+10분)까지. 시계가 초기화된 카메라(1980년)·앞서 간 시계·현지 시각을 UTC로 적은 영상(미래가 됨)은
 * 버리고 파일 시각을 쓴다(정보 수정 화면의 날짜 범위 2000년~오늘 밖이면 저장이 막히므로) */
export const plausible = (ms: number) => ms >= Date.UTC(2001, 0, 1) && ms <= Date.now() + 600_000;

async function readPhoto(file: Blob): Promise<string | null> {
  const x = await tiffOf(file);
  return x ? readTiff(x.v, x.t, x.end) : null;
}

/** 사진 파일 안 EXIF(TIFF)의 자리: HEIC Exif 항목·PNG eXIf·JPEG APP1. 없으면 null */
async function tiffOf(file: Blob): Promise<{ v: DataView; t: number; end: number } | null> {
  const buf = await file.slice(0, HEAD).arrayBuffer();
  const v = new DataView(buf);
  if (v.byteLength >= 12 && v.getUint32(4) === 0x66747970) {
    // ISO 상자 'ftyp' → HEIC/HEIF
    const at = heifExif(v);
    if (!at || at.length < 8) return null;
    const ex = new DataView(await file.slice(at.offset, at.offset + Math.min(at.length, HEAD)).arrayBuffer());
    if (ex.byteLength < 8) return null;
    // Exif 항목: 앞 4바이트는 TIFF 머리까지 건너뛸 길이(보통 'Exif\0\0' 6바이트)
    const t = 4 + ex.getUint32(0);
    return t + 8 <= ex.byteLength ? { v: ex, t, end: ex.byteLength } : null;
  }
  if (v.byteLength >= 8 && v.getUint32(0) === 0x89504e47 && v.getUint32(4) === 0x0d0a1a0a) return pngTiff(v);
  return jpegTiff(v);
}

/** PNG 'eXIf' 덩어리(내용이 바로 TIFF) */
function pngTiff(v: DataView): { v: DataView; t: number; end: number } | null {
  let p = 8;
  while (p + 8 <= v.byteLength) {
    const len = v.getUint32(p);
    const type = v.getUint32(p + 4);
    if (type === 0x65584966) return { v, t: p + 8, end: Math.min(v.byteLength, p + 8 + len) };
    if (type === 0x49444154 || type === 0x49454e44) return null; // IDAT·IEND: 그림 시작·끝, eXIf는 그 앞에 온다
    p += 12 + len;
  }
  return null;
}

/** HEIF 'meta' 상자에서 Exif 항목의 파일 안 위치(iinf로 항목 번호, iloc으로 자리). 못 찾으면 null */
function heifExif(v: DataView): { offset: number; length: number } | null {
  /** [start, stop) 안의 상자들 → [이름, 내용 시작, 끝] */
  const boxes = (start: number, stop: number) => {
    const out: [string, number, number][] = [];
    let p = start;
    while (p + 8 <= stop) {
      let size = v.getUint32(p);
      let head = 8;
      if (size === 1) {
        if (p + 16 > stop) break;
        size = Number(v.getBigUint64(p + 8));
        head = 16;
      } else if (size === 0) size = stop - p;
      if (size < head) break;
      out.push([String.fromCharCode(v.getUint8(p + 4), v.getUint8(p + 5), v.getUint8(p + 6), v.getUint8(p + 7)), p + head, Math.min(stop, p + size)]);
      p += size;
    }
    return out;
  };
  const get = (list: [string, number, number][], name: string) => list.find((x) => x[0] === name);
  const meta = get(boxes(0, v.byteLength), 'meta');
  if (!meta) return null;
  const kids = boxes(meta[1] + 4, meta[2]); // meta는 FullBox(버전·플래그 4바이트)
  const iinf = get(kids, 'iinf');
  const iloc = get(kids, 'iloc');
  if (!iinf || !iloc) return null;
  // 범위 밖 읽기는 RangeError → 아래 try에서 null
  try {
    // iinf: 항목 정보(infe) 중 종류가 'Exif'인 것의 번호
    let p = iinf[1];
    p += 4 + (v.getUint8(p) === 0 ? 2 : 4);
    let id = -1;
    for (const [type, s, e] of boxes(p, iinf[2])) {
      if (type !== 'infe' || e - s < 12) continue;
      const ver = v.getUint8(s);
      if (ver < 2) continue;
      const q = s + 4;
      const item = ver === 2 ? v.getUint16(q) : v.getUint32(q);
      const kind = v.getUint32(q + (ver === 2 ? 4 : 6));
      if (kind === 0x45786966) {
        id = item;
        break;
      }
    }
    if (id < 0) return null;
    // iloc: 항목 번호 → (자리, 길이). 방식 0은 파일 안 자리, 1은 meta 안 idat 안 자리
    p = iloc[1];
    const ver = v.getUint8(p);
    p += 4;
    const sizes = v.getUint8(p);
    const sizes2 = v.getUint8(p + 1);
    p += 2;
    const offSize = sizes >> 4, lenSize = sizes & 15, baseSize = sizes2 >> 4, idxSize = ver === 1 || ver === 2 ? sizes2 & 15 : 0;
    const num = (n: number) => {
      const x = n === 0 ? 0 : n === 4 ? v.getUint32(p) : n === 8 ? Number(v.getBigUint64(p)) : NaN;
      p += n;
      return x;
    };
    if (lenSize === 0) return null; // 길이 없는 자리는 못 읽는다(크기 0이면 아래 루프가 제자리를 돈다)
    const count = ver < 2 ? (p += 2, v.getUint16(p - 2)) : (p += 4, v.getUint32(p - 4));
    for (let i = 0; i < count && p < iloc[2]; i++) {
      const item = ver < 2 ? (p += 2, v.getUint16(p - 2)) : (p += 4, v.getUint32(p - 4));
      const method = ver === 1 || ver === 2 ? (p += 2, v.getUint16(p - 2) & 15) : 0;
      p += 2; // data_reference_index
      const base = num(baseSize);
      const extents = (p += 2, v.getUint16(p - 2));
      if (p + extents * (idxSize + offSize + lenSize) > iloc[2]) return null;
      let first: { offset: number; length: number } | null = null;
      for (let j = 0; j < extents; j++) {
        num(idxSize);
        const off = num(offSize);
        const len = num(lenSize);
        first ??= { offset: base + off, length: len };
      }
      if (item !== id) continue;
      if (!first || !Number.isFinite(first.offset) || !Number.isFinite(first.length)) return null;
      if (method === 0) return first;
      const idat = get(kids, 'idat');
      return method === 1 && idat ? { offset: idat[1] + first.offset, length: first.length } : null;
    }
    return null;
  } catch {
    return null;
  }
}

/** MP4·MOV 'moov/mvhd'의 만든 시각(UTC, 1904년부터 초). 믿을 만한 범위(plausible) 밖이면 null.
 * 안드로이드 일부는 현지 시각을 UTC처럼 적어 몇 시간 늦게 보일 수 있다(미래가 되면 버려짐) */
export async function mp4CreatedAt(file: Blob): Promise<string | null> {
  let p = 0;
  // 위 단계 상자(ftyp·mdat·moov…)를 머리만 읽으며 건너뛴다. moov는 앞에도 끝에도 올 수 있다
  for (let i = 0; i < 64 && p + 8 <= file.size; i++) {
    const h = new DataView(await file.slice(p, p + 16).arrayBuffer());
    let size = h.getUint32(0);
    let head = 8;
    if (size === 1 && h.byteLength >= 16) {
      size = Number(h.getBigUint64(8));
      head = 16;
    } else if (size === 0) size = file.size - p;
    if (size < head) return null;
    if (h.getUint32(4) === 0x6d6f6f76) {
      // moov 안 첫 상자들 중 mvhd(보통 맨 앞)
      const m = new DataView(await file.slice(p + head, p + Math.min(size, head + 4096)).arrayBuffer());
      let q = 0;
      while (q + 8 <= m.byteLength) {
        const n = m.getUint32(q);
        if (m.getUint32(q + 4) === 0x6d766864 && q + 16 <= m.byteLength) {
          const ver = m.getUint8(q + 8);
          const secs = ver === 1 ? (q + 20 <= m.byteLength ? Number(m.getBigUint64(q + 12)) : NaN) : m.getUint32(q + 12);
          const ms = (secs - 2082844800) * 1000;
          return plausible(ms) ? new Date(ms).toISOString() : null;
        }
        if (n < 8) return null;
        q += n;
      }
      return null;
    }
    p += size;
  }
  return null;
}

/** DateTimeOriginal(+OffsetTimeOriginal)을 ISO 시각으로. 시간대가 없으면 한국 시간(+09:00)으로 본다. 없거나 깨졌으면 null */
export function exifTakenAt(buf: ArrayBuffer): string | null {
  const x = jpegTiff(new DataView(buf));
  return x ? readTiff(x.v, x.t, x.end) : null;
}

/** JPEG APP1 'Exif\0\0' 안 TIFF 자리 */
function jpegTiff(v: DataView): { v: DataView; t: number; end: number } | null {
  if (v.byteLength < 4 || v.getUint16(0) !== 0xffd8) return null;
  let p = 2;
  while (p + 4 <= v.byteLength) {
    const marker = v.getUint16(p);
    const len = v.getUint16(p + 2);
    if ((marker & 0xff00) !== 0xff00 || len < 2) return null;
    if (marker === 0xffe1 && p + 10 <= v.byteLength && v.getUint32(p + 4) === 0x45786966 && v.getUint16(p + 8) === 0) {
      return { v, t: p + 10, end: Math.min(v.byteLength, p + 2 + len) };
    }
    if (marker === 0xffda) return null; // 이미지 데이터 시작: EXIF 없음
    p += 2 + len;
  }
  return null;
}

// 옮겨 적는 정보(142, 사용자 "위치정보만 지우고 찍은날 정보는 두면"): 위치(GPS)·회전·작은 그림·제조사 메모(MakerNote)는 빼고 아래만.
// 빼고 싶은 걸 고르는 대신 남길 것만 골라 적는다(모르는 태그에 위치가 숨어 있어도 따라가지 않게)
const KEEP_IFD0 = [0x010f, 0x0110, 0x0131, 0x0132]; // 제조사·기종·소프트웨어·수정 시각
const KEEP_EXIF = [
  0x829a, 0x829d, 0x8827, 0x9003, 0x9004, 0x9010, 0x9011, 0x9012, 0x9204, 0x9209, 0x920a, 0x9290, 0x9291, 0x9292, 0xa405, 0xa433, 0xa434,
]; // 노출·조리개·ISO·찍은 시각·시간대·노출 보정·플래시·초점 거리·렌즈
const UNIT: Record<number, number> = { 1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8 };
type Entry = { tag: number; type: number; count: number; bytes: Uint8Array };

/** 사진 파일의 정보 중 남길 것만 담은 JPEG APP1(EXIF) 덩어리. 정보가 없으면 null */
export async function photoExif(file: Blob): Promise<Uint8Array | null> {
  const x = await tiffOf(file);
  if (!x) return null;
  const { v, t, end } = x;
  const le = v.getUint16(t) === 0x4949;
  if (!le && v.getUint16(t) !== 0x4d4d) return null;
  const pick = (ifd: number, keep: number[]): Entry[] => {
    const out: Entry[] = [];
    if (!(ifd >= 8) || t + ifd + 2 > end) return out;
    const n = v.getUint16(t + ifd, le);
    for (let i = 0; i < n && i < 512; i++) {
      const e = t + ifd + 2 + i * 12;
      if (e + 12 > end) break;
      const tag = v.getUint16(e, le), type = v.getUint16(e + 2, le), count = v.getUint32(e + 4, le);
      if (!keep.includes(tag) || !UNIT[type]) continue;
      const size = count * UNIT[type];
      if (size > 256) continue;
      const at = size > 4 ? t + v.getUint32(e + 8, le) : e + 8;
      if (at + size > end) continue;
      out.push({ tag, type, count, bytes: new Uint8Array(v.buffer, v.byteOffset + at, size).slice() });
    }
    return out;
  };
  const ifd0 = v.getUint32(t + 4, le);
  const top = pick(ifd0, KEEP_IFD0);
  let exifAt = -1;
  if (ifd0 >= 8 && t + ifd0 + 2 <= end) {
    const n = v.getUint16(t + ifd0, le);
    for (let i = 0; i < n; i++) {
      const e = t + ifd0 + 2 + i * 12;
      if (e + 12 > end) break;
      if (v.getUint16(e, le) === 0x8769) exifAt = v.getUint32(e + 8, le);
    }
  }
  const sub = exifAt > 0 ? pick(exifAt, KEEP_EXIF) : [];
  if (!top.length && !sub.length) return null;
  const tiff = writeTiff(le, top, sub);
  const app1 = new Uint8Array(10 + tiff.length);
  const w = new DataView(app1.buffer);
  w.setUint16(0, 0xffe1);
  w.setUint16(2, 8 + tiff.length);
  app1.set([0x45, 0x78, 0x69, 0x66, 0, 0], 4);
  app1.set(tiff, 10);
  return app1;
}

/** IFD0(+Exif IFD 포인터)와 Exif IFD만 있는 TIFF. 값은 원래 바이트 순서 그대로 옮긴다 */
function writeTiff(le: boolean, top: Entry[], sub: Entry[]): Uint8Array {
  const ifdSize = (n: number) => 2 + n * 12 + 4;
  const dataSize = (list: Entry[]) => list.reduce((a, x) => a + (x.bytes.length > 4 ? (x.bytes.length + 1) & ~1 : 0), 0);
  const nTop = top.length + (sub.length ? 1 : 0);
  const ifd0 = 8, data0 = ifd0 + ifdSize(nTop), exif = data0 + dataSize(top), data1 = exif + ifdSize(sub.length);
  const out = new Uint8Array(data1 + dataSize(sub));
  const w = new DataView(out.buffer);
  w.setUint16(0, le ? 0x4949 : 0x4d4d);
  w.setUint16(2, 42, le);
  w.setUint32(4, ifd0, le);
  const put = (at: number, list: Entry[], data: number, extra?: Entry) => {
    const all = [...list, ...(extra ? [extra] : [])].sort((a, b) => a.tag - b.tag);
    w.setUint16(at, all.length, le);
    all.forEach((x, i) => {
      const e = at + 2 + i * 12;
      w.setUint16(e, x.tag, le);
      w.setUint16(e + 2, x.type, le);
      w.setUint32(e + 4, x.count, le);
      if (x.bytes.length > 4) {
        w.setUint32(e + 8, data, le);
        out.set(x.bytes, data);
        data += (x.bytes.length + 1) & ~1;
      } else out.set(x.bytes, e + 8);
    });
    w.setUint32(at + 2 + all.length * 12, 0, le); // 다음 IFD 없음(작은 그림 IFD1 안 옮김)
  };
  const ptr = new Uint8Array(4);
  new DataView(ptr.buffer).setUint32(0, exif, le);
  put(ifd0, top, data0, sub.length ? { tag: 0x8769, type: 4, count: 1, bytes: ptr } : undefined);
  if (sub.length) put(exif, sub, data1);
  return out;
}

/** JPEG에 APP1을 넣는다(JFIF APP0이 있으면 그 뒤, 없으면 SOI 바로 뒤) */
export function withExif(jpeg: Uint8Array, app1: Uint8Array): Uint8Array<ArrayBuffer> {
  let p = 2;
  if (jpeg[2] === 0xff && jpeg[3] === 0xe0) p = 4 + ((jpeg[4] << 8) | jpeg[5]);
  const out = new Uint8Array(jpeg.length + app1.length);
  out.set(jpeg.subarray(0, p));
  out.set(app1, p);
  out.set(jpeg.subarray(p), p + app1.length);
  return out;
}

function readTiff(v: DataView, t: number, end: number): string | null {
  if (t + 8 > end) return null;
  const le = v.getUint16(t) === 0x4949;
  if (!le && v.getUint16(t) !== 0x4d4d) return null;
  // 범위 밖이면 NaN을 돌려 아래 검사에서 걸러지게(이상한 파일에서 예외가 나지 않게)
  const u16 = (o: number) => (t + o + 2 <= end ? v.getUint16(t + o, le) : NaN);
  const u32 = (o: number) => (t + o + 4 <= end ? v.getUint32(t + o, le) : NaN);
  const ascii = (o: number, n: number) => {
    let s = '';
    for (let i = 0; i < n && t + o + i < end; i++) {
      const c = v.getUint8(t + o + i);
      if (c === 0) break;
      s += String.fromCharCode(c);
    }
    return s;
  };
  // 형식별 한 개 크기: 2 ASCII 1바이트, 4 LONG·13 IFD 4바이트
  const SIZE: Record<number, number> = { 2: 1, 4: 4, 13: 4 };
  /** IFD에서 태그(기대 형식만) → (개수, 값 위치). 값이 4바이트 넘으면 위치는 포인터 */
  const find = (ifd: number, tag: number, types: number[]): { count: number; at: number } | null => {
    const n = u16(ifd);
    if (!(n >= 0) || n > 512) return null;
    for (let i = 0; i < n; i++) {
      const e = ifd + 2 + i * 12;
      if (t + e + 12 > end) return null;
      if (u16(e) !== tag) continue;
      const type = u16(e + 2);
      const count = u32(e + 4);
      if (!types.includes(type) || !(count >= 0)) return null;
      const at = count * SIZE[type] > 4 ? u32(e + 8) : e + 8;
      return Number.isFinite(at) ? { count, at } : null;
    }
    return null;
  };
  const ifd0 = u32(4);
  if (!Number.isFinite(ifd0)) return null;
  const exifPtr = find(ifd0, 0x8769, [4, 13]);
  if (!exifPtr) return null;
  const exif = u32(exifPtr.at);
  if (!Number.isFinite(exif)) return null;
  const dto = find(exif, 0x9003, [2]);
  if (!dto) return null;
  const m = /^(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})$/.exec(ascii(dto.at, dto.count));
  if (!m || m[1] === '0000') return null;
  const off = find(exif, 0x9011, [2]);
  const tz = off && /^[+-]\d{2}:\d{2}$/.test(ascii(off.at, off.count)) ? ascii(off.at, off.count) : '+09:00';
  const d = new Date(`${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}${tz}`);
  return Number.isNaN(d.getTime()) ? null : d.toISOString();
}

/** JPEG에서 위치·기기 정보를 화질 손실 없이 뺀 바이트. 남기는 것: APP0 JFIF·APP2 색 정보(ICC)·APP14(Adobe 색 변환)·그림 데이터.
 * 빼는 것: APP1(EXIF·XMP, GPS가 여기)·다른 APP·주석·EOI 뒤에 붙은 데이터(스캔 사이에 온 것도). 회전 정보(Orientation≠1)가 있거나 깨졌으면 null(다시 저장해야 함) */
export function stripJpeg(buf: ArrayBuffer): Uint8Array<ArrayBuffer> | null {
  const b = new Uint8Array(buf);
  const v = new DataView(buf);
  if (b.length < 4 || v.getUint16(0) !== 0xffd8) return null;
  const keep: Uint8Array[] = [b.subarray(0, 2)];
  let p = 2;
  while (p + 2 <= b.length) {
    const marker = v.getUint16(p);
    if ((marker & 0xff00) !== 0xff00) return null;
    if (marker === 0xffff) { p++; continue; } // 채움 바이트
    if (marker === 0xffd9) {
      keep.push(b.subarray(p, p + 2));
      const out = new Uint8Array(keep.reduce((n, x) => n + x.length, 0));
      let o = 0;
      for (const x of keep) (out.set(x, o), (o += x.length));
      return out;
    }
    // 길이 없는 표지(TEM·RSTn)는 그림 데이터 밖에 오면 깨진 파일
    if (marker === 0xff01 || (marker >= 0xffd0 && marker <= 0xffd8) || p + 4 > b.length) return null;
    const len = v.getUint16(p + 2);
    if (len < 2 || p + 2 + len > b.length) return null;
    let end = p + 2 + len;
    if (marker === 0xffda) {
      // 그림 데이터: FF 뒤에 00·RSTn·채움이면 데이터, 아니면 다음 표지(프로그레시브는 스캔 사이에 표지가 온다)
      while (end + 1 < b.length && !(b[end] === 0xff && b[end + 1] !== 0x00 && b[end + 1] !== 0xff && (b[end + 1] < 0xd0 || b[end + 1] > 0xd7))) end++;
      if (end + 1 >= b.length) return null;
    }
    const app = marker >= 0xffe0 && marker <= 0xffef;
    if (marker === 0xffe1 && len >= 8 && v.getUint32(p + 4) === 0x45786966 && orientation(v, p + 10, p + 2 + len) > 1) return null;
    const icc = marker === 0xffe2 && len >= 14 && String.fromCharCode(...b.subarray(p + 4, p + 15)) === 'ICC_PROFILE';
    // APP0은 JFIF만(JFXX엔 잘리기 전 작은 그림이 들 수 있다)
    const jfif = marker === 0xffe0 && len >= 7 && v.getUint32(p + 4) === 0x4a464946 && b[p + 8] === 0;
    if (!(app || marker === 0xfffe) || jfif || marker === 0xffee || icc) keep.push(b.subarray(p, end));
    p = end;
  }
  return null;
}

/** TIFF IFD0의 Orientation(0x0112). 없으면 1, 깨졌으면 9(다시 저장하게) */
function orientation(v: DataView, t: number, end: number): number {
  if (t + 8 > end) return 9;
  const le = v.getUint16(t) === 0x4949;
  if (!le && v.getUint16(t) !== 0x4d4d) return 9;
  const ifd = t + v.getUint32(t + 4, le);
  if (ifd + 2 > end) return 9;
  const n = v.getUint16(ifd, le);
  for (let i = 0; i < n; i++) {
    const e = ifd + 2 + i * 12;
    if (e + 12 > end) return 9;
    // 보통 SHORT(3), 잘못 만든 파일은 LONG(4)
    if (v.getUint16(e, le) === 0x0112) return v.getUint16(e + 2, le) === 4 ? v.getUint32(e + 8, le) : v.getUint16(e + 8, le);
  }
  return 1;
}

/** 긴 변을 max 이하로 줄인 크기(늘리지는 않는다) */
export function fitSize(w: number, h: number, max: number): { width: number; height: number } {
  const k = Math.min(1, max / Math.max(w, h));
  return { width: Math.max(1, Math.round(w * k)), height: Math.max(1, Math.round(h * k)) };
}
