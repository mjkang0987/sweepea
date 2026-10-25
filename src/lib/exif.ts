// JPEG EXIF에서 촬영 시각만 읽는다(라이브러리 없이). 사진 파일 앞부분(128KB 정도)이면 충분하다

/** DateTimeOriginal(+OffsetTimeOriginal)을 ISO 시각으로. 시간대가 없으면 한국 시간(+09:00)으로 본다. 없거나 깨졌으면 null */
export function exifTakenAt(buf: ArrayBuffer): string | null {
  const v = new DataView(buf);
  if (v.byteLength < 4 || v.getUint16(0) !== 0xffd8) return null;
  let p = 2;
  while (p + 4 <= v.byteLength) {
    const marker = v.getUint16(p);
    const len = v.getUint16(p + 2);
    if ((marker & 0xff00) !== 0xff00 || len < 2) return null;
    // APP1 'Exif\0\0'
    if (marker === 0xffe1 && p + 10 <= v.byteLength && v.getUint32(p + 4) === 0x45786966 && v.getUint16(p + 8) === 0) {
      return readTiff(v, p + 10, Math.min(v.byteLength, p + 2 + len));
    }
    if (marker === 0xffda) return null; // 이미지 데이터 시작: EXIF 없음
    p += 2 + len;
  }
  return null;
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

/** 긴 변을 max 이하로 줄인 크기(늘리지는 않는다) */
export function fitSize(w: number, h: number, max: number): { width: number; height: number } {
  const k = Math.min(1, max / Math.max(w, h));
  return { width: Math.max(1, Math.round(w * k)), height: Math.max(1, Math.round(h * k)) };
}
