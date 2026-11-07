// 영상 찍은 장소 지우기(138, 개인정보): 영상의 위치(moov 안 ©xyz 글자 상자, 3GPP loci 숫자 상자, mdta 키 'com.apple.quicktime.location.*'의 값)를
// 0으로 덮고 상자 이름을 free로 바꾼다. 크기·자리가 그대로라 영상 구조(mdat 위치 등)는 안 바뀐다. moov만 읽어 큰 영상도 메모리 걱정 없음

const type4 = (s: string) => ((s.charCodeAt(0) << 24) | (s.charCodeAt(1) << 16) | (s.charCodeAt(2) << 8) | s.charCodeAt(3)) >>> 0;
const MOOV = type4('moov'), XYZ = 0xa978797a /* ©xyz */, LOCI = type4('loci'), META = type4('meta'), HDLR = type4('hdlr'), KEYS = type4('keys'), ILST = type4('ilst'), FREE = type4('free');
const CONTAINERS = new Set([type4('trak'), type4('udta')]);
// shortcut: moov가 이보다 크면(아주 긴 영상) 지우지 않고 그대로 둔다, 그런 영상이 실제로 나오면 moov를 나눠 읽기
const MOOV_MAX = 64 * 1024 * 1024;

/** 상자 머리: [크기, 머리 길이]. 깨졌으면 null */
function box(dv: DataView, p: number, end: number): [number, number] | null {
  if (p + 8 > end) return null;
  let size = dv.getUint32(p);
  let head = 8;
  if (size === 1) {
    if (p + 16 > end) return null;
    size = Number(dv.getBigUint64(p + 8));
    head = 16;
  } else if (size === 0) size = end - p;
  return size < head || p + size > end ? null : [size, head];
}

function kill(b: Uint8Array, dv: DataView, p: number, size: number, head: number) {
  b.fill(0, p + head, p + size);
  dv.setUint32(p + 4, FREE);
}

/** meta 안: keys에서 위치 키 번호를 찾아 그 이름을 지우고, ilst에서 같은 번호 값 상자를 지운다 */
function scrubMeta(b: Uint8Array, dv: DataView, start: number, end: number): number {
  const hit = new Set<number>();
  let n = 0;
  for (let p = start, h; (h = box(dv, p, end)); p += h[0]) {
    if (dv.getUint32(p + 4) !== KEYS) continue;
    let q = p + h[1] + 8; // version·flags 4 + 개수 4
    for (let i = 1; q + 8 <= p + h[0]; i++) {
      const len = dv.getUint32(q);
      if (len < 8 || q + len > p + h[0]) break;
      const name = new TextDecoder().decode(b.subarray(q + 8, q + len));
      if (name.includes('location')) {
        hit.add(i);
        b.fill(0x78, q + 8, q + len); // 이름은 'xxxx…'(같은 길이)
      }
      q += len;
    }
  }
  if (!hit.size) return 0;
  for (let p = start, h; (h = box(dv, p, end)); p += h[0]) {
    if (dv.getUint32(p + 4) !== ILST) continue;
    for (let q = p + h[1], g; (g = box(dv, q, p + h[0])); q += g[0]) {
      if (hit.has(dv.getUint32(q + 4))) {
        kill(b, dv, q, g[0], g[1]);
        n++;
      }
    }
  }
  return n + hit.size;
}

/** moov 내용(머리 뺀 것)을 그 자리에서 고친다. 지운 항목 수 */
export function scrubMoov(b: Uint8Array, start = 0, end = b.byteLength): number {
  const dv = new DataView(b.buffer, b.byteOffset, b.byteLength);
  let n = 0;
  for (let p = start, h; (h = box(dv, p, end)); p += h[0]) {
    const t = dv.getUint32(p + 4);
    if (t === XYZ || t === LOCI) {
      kill(b, dv, p, h[0], h[1]);
      n++;
    } else if (CONTAINERS.has(t)) n += scrubMoov(b, p + h[1], p + h[0]);
    else if (t === META) {
      // QuickTime meta는 바로 상자들, ISO meta는 version·flags 4바이트 뒤(첫 상자가 hdlr인지로 가림)
      const q = p + h[1];
      const iso = !(q + 8 <= p + h[0] && dv.getUint32(q + 4) === HDLR);
      n += scrubMeta(b, dv, iso ? q + 4 : q, p + h[0]);
    }
  }
  return n;
}

/** 위치를 지운 영상(없으면 받은 그대로). mp4·mov(위 단계 상자를 머리만 읽으며 moov를 찾음) */
export async function stripVideoLocation(file: Blob): Promise<Blob> {
  let p = 0;
  for (let i = 0; i < 64 && p + 8 <= file.size; i++) {
    // 위 단계 상자는 머리(16바이트)만 읽는다
    const dv = new DataView(await file.slice(p, p + 16).arrayBuffer());
    let size = dv.getUint32(0);
    let head = 8;
    if (size === 1 && dv.byteLength >= 16) {
      size = Number(dv.getBigUint64(8));
      head = 16;
    } else if (size === 0) size = file.size - p;
    if (size < head) return file;
    if (dv.getUint32(4) === MOOV) {
      if (size > MOOV_MAX || p + size > file.size) return file;
      const moov = new Uint8Array(await file.slice(p, p + size).arrayBuffer());
      if (!scrubMoov(moov, head, size)) return file;
      return new Blob([file.slice(0, p), moov, file.slice(p + size)], { type: file.type });
    }
    p += size;
  }
  return file;
}
