// src/data.js
export function parseCsv(text) {            // RFC 4180: 따옴표 안의 쉼표·줄바꿈·"" 처리
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (c === '"') q = false; else cell += c; }
    else if (c === '"') q = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += c;
  }
  if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
  const [head, ...body] = rows.filter(r => r.length > 1 || r[0] !== '');
  return body.map(r => Object.fromEntries(head.map((h, i) => [h, r[i] ?? ''])));
}

const CAST = { int: v => parseInt(v, 10), float: v => parseFloat(v), string: v => v, bool: v => v === 'true' || v === '1' };

export async function loadBalance(table, schema) {   // schema = data/balance/_schema.json 전체
  const rows = parseCsv(await (await fetch(`../data/balance/${table}.csv`)).text());
  const cols = schema[table]?.columns ?? {};
  const byId = {};
  for (const r of rows) {
    for (const [c, spec] of Object.entries(cols)) {
      const v = CAST[spec.type ?? 'string'](r[c]);
      if ((spec.type === 'int' || spec.type === 'float') && (Number.isNaN(v) || (spec.min != null && v < spec.min)))
        throw new Error(`밸런스 값 오류 ${table}.${r.id}.${c}=${r[c]}`);   // 조용히 넘어가지 않는다
      r[c] = v;
    }
    byId[r.id] = r;
  }
  return byId;
}

let STR = {}, FALLBACK = {};
export async function loadStrings(lang) {
  FALLBACK = await (await fetch('../data/strings/ko.json')).json();
  STR = lang === 'ko' ? FALLBACK : await fetch(`../data/strings/${lang}.json`).then(r => r.ok ? r.json() : {});
}
export function t(key, vars = {}) {
  let s = STR[key];
  if (s == null) { s = FALLBACK[key]; window.__game?.missingStrings.add(key); }
  if (s == null) return key;                                  // 키 이름을 그대로 보여 준다
  return s.replace(/\{([a-zA-Z_]\w*)\}/g, (_, k) => vars[k] ?? `{${k}}`);
}
