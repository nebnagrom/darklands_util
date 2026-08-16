// Darklands save-file (DKSAVE*.SAV) parsing helpers.
// Ported from src/main/python/list_quests.py and alchemy_profit.py.
// Plain JS (no JSX) so it can be shared via <script src> across pages.

// Matches Python's `{:.0f}` formatting (round-half-to-even), used for
// alchemy_profit.py's success% and expected-profit columns so exact .5
// ties (e.g. 54.5) display identically to the Python tool.
function roundHalfEven(x) {
  const floor = Math.floor(x);
  const diff = x - floor;
  if (diff < 0.5) return floor;
  if (diff > 0.5) return floor + 1;
  return (floor % 2 === 0) ? floor : floor + 1;
}

function decodeDarklandString(bytes) {
  let end = bytes.indexOf(0);
  if (end === -1) end = bytes.length;
  let s = '';
  for (let i = 0; i < end; i++) {
    let b = bytes[i];
    // Darklands uses 0x7b for ö and 0x7c for ü (neither CP437 nor latin-1)
    if (b === 0x7b) b = 0xf6;
    else if (b === 0x7c) b = 0xfc;
    s += String.fromCharCode(b);
  }
  return s;
}

function parseSaveQuests(arrayBuffer, lstItems) {
  const buf = new Uint8Array(arrayBuffer);
  const view = new DataView(arrayBuffer);

  const QUEST_SZ = 48, LOC_SZ = 58, LOC_NAME_SZ = 20, CHAR_SZ = 554, CHARS_START = 393;
  const OFF_YEAR = 104, OFF_NUM_CHARS = 241;
  const MAX_LOC = 420, CITY_COUNT = 92;
  const WHO = ["Merchant", "#1", "#2", "#3", "Foreign Trader", "Pharmacist", "Medici",
    "Hanseatic League", "Fugger", "Schulz", "Mayor", "#11"];
  const NSEW = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

  function locName(locBuf, idx) {
    if (idx < 0 || idx >= locBuf.length) return '<invalid index>';
    return decodeDarklandString(locBuf[idx].subarray(38, 38 + LOC_NAME_SZ));
  }
  function locCoords(locBuf, idx) {
    const rec = locBuf[idx];
    const dv = new DataView(rec.buffer, rec.byteOffset, rec.byteLength);
    return [dv.getInt16(4, true), dv.getInt16(6, true)];
  }
  function compass(sx, sy, cx, cy) {
    let dx = Math.abs(sx - cx), dy = Math.abs(sy - cy);
    if (dx === 0) dx = 0.0001;
    const angle = Math.atan2(dy, dx);
    if (angle < Math.PI / 8) return sx > cx ? 2 : 6;
    if (angle < Math.PI * 3 / 8) {
      return sx > cx ? (sy < cy ? 1 : 3) : (sy > cy ? 5 : 7);
    }
    return sy < cy ? 0 : 4;
  }
  function closestCity(locBuf, idx, exclude) {
    const [sx, sy] = locCoords(locBuf, idx);
    let bestDist = Infinity, bestI = -1, bestCx = 0, bestCy = 0;
    for (let i = 0; i < Math.min(CITY_COUNT, locBuf.length); i++) {
      if (i === exclude) continue;
      const [cx, cy] = locCoords(locBuf, i);
      const d = Math.hypot(cx - sx, cy - sy);
      if (d < bestDist) { bestDist = d; bestI = i; bestCx = cx; bestCy = cy; }
    }
    return [bestI, compass(sx, sy, bestCx, bestCy)];
  }

  const year = view.getUint16(OFF_YEAR, true);
  const month = view.getUint16(OFF_YEAR + 2, true) + 1;
  const day = view.getUint16(OFF_YEAR + 4, true);
  const hour = view.getUint16(OFF_YEAR + 6, true);
  const numChars = view.getUint16(OFF_NUM_CHARS, true);

  const questNumOff = CHARS_START + numChars * CHAR_SZ;
  const numQuests = view.getInt16(questNumOff, true);
  const firstQuestOff = questNumOff + 2;

  const locNumOff = firstQuestOff + numQuests * QUEST_SZ;
  const numLoc = Math.min(view.getInt16(locNumOff, true), MAX_LOC);
  const locStart = locNumOff + 2;
  const locBuf = [];
  for (let i = 0; i < numLoc; i++) {
    locBuf.push(buf.subarray(locStart + i * LOC_SZ, locStart + (i + 1) * LOC_SZ));
  }

  const pad2 = n => String(n).padStart(2, '0');

  const quests = [];
  let pending = 0;
  for (let i = 0; i < numQuests; i++) {
    const qOff = firstQuestOff + i * QUEST_SZ;
    const q = [];
    for (let k = 0; k < 24; k++) q.push(view.getInt16(qOff + k * 2, true));

    const startD = q[6], startM = q[7], startY = q[8];
    const dlD = q[10], dlM = q[11], dlY = q[12];
    const employer = q[13], destIdx = q[14], repoIdx = q[15], itemIdx = q[23];

    if (employer < 0 || dlY === startY) continue;
    if (!(q[17] === 8 && q[21] !== 0 && q[22] === 2) && q[17] !== 36) {
      if (itemIdx === 0) continue;
    }

    pending++;
    const who = (employer >= 0 && employer < WHO.length) ? WHO[employer] : `#${employer}`;

    let line1 = '';
    if (itemIdx !== 0) {
      const iname = (itemIdx < lstItems.length) ? lstItems[itemIdx].name : `#item${itemIdx}`;
      line1 += (dlY === 1499) ? `Get ${iname} from ` : `Return ${iname} to ${who} at `;
    } else {
      line1 += 'Raubritter Quest - go to - ';
    }
    line1 += `${locName(locBuf, destIdx)} `;

    if (destIdx > 91) {
      const [c1, dir1] = closestCity(locBuf, destIdx, -1);
      const [c2, dir2] = closestCity(locBuf, destIdx, c1);
      line1 += `(${NSEW[dir1]} of ${locName(locBuf, c1)}, ${NSEW[dir2]} of ${locName(locBuf, c2)}) `;
    }

    if (dlY > 1498) {
      line1 += `[from ${startY}/${pad2(startM + 1)}/${pad2(startD)}]`;
    } else {
      line1 += `by ${dlY}/${pad2(dlM + 1)}/${pad2(dlD)}`;
    }

    let line2 = null;
    const repoName = locName(locBuf, repoIdx);
    if (itemIdx !== 0) {
      if (dlY === 1499) line2 = `Deliver to ${who} at ${repoName}`;
    } else {
      line2 = `Report to ${who} at ${repoName}`;
    }

    quests.push({ num: pending, line1, line2 });
  }

  return { year, month, day, hour, quests, pending };
}

function parseSaveAlchemy(arrayBuffer, formulaTable, formulaTypes, potionsMap) {
  const view = new DataView(arrayBuffer);
  const buf = new Uint8Array(arrayBuffer);

  const PSTONE_OFF = 0x92, PARTY_INDICES_OFF = 0xF3, NUM_CHARS_OFF = 0xF1;
  const CHARS_OFF = 0x189, CHAR_SIZE = 554;
  const CHR_NAME_OFF = 0x25, CHR_ATTRS_OFF = 0x5D, CHR_SKILLS_OFF = 0x6B, CHR_FORMS_OFF = 0x94;
  const INT_ATTR_IDX = 4, ALCH_SKILL_IDX = 7;
  const Q_TIERS = [[25, 0x01, 0], [35, 0x02, 1], [45, 0x04, 2]];
  const TRANSFORMATION_BONUS_PF = 240;

  const pstone = view.getUint16(PSTONE_OFF, true);

  const partyIndices = new Set();
  for (let i = 0; i < 5; i++) {
    const v = view.getUint16(PARTY_INDICES_OFF + i * 2, true);
    if (v !== 0xFFFF) partyIndices.add(v);
  }

  const numChars = view.getUint16(NUM_CHARS_OFF, true);
  const characters = [];
  for (let i = 0; i < numChars; i++) {
    if (!partyIndices.has(i)) continue;
    const base = CHARS_OFF + i * CHAR_SIZE;
    const nameBytes = buf.subarray(base + CHR_NAME_OFF, base + CHR_NAME_OFF + 25);
    const name = decodeDarklandString(nameBytes).trim() || `Character ${i}`;
    const intelligence = buf[base + CHR_ATTRS_OFF + INT_ATTR_IDX];
    const alchemy = buf[base + CHR_SKILLS_OFF + ALCH_SKILL_IDX];
    const formsRaw = buf.subarray(base + CHR_FORMS_OFF, base + CHR_FORMS_OFF + 22);
    characters.push({ name, intelligence, alchemy, formsRaw });
  }

  const results = characters.filter(c => c.alchemy > 0).map(char => {
    const total = char.alchemy + char.intelligence + pstone;
    const brewable = [], impossible = [], unmatched = [];

    for (let typeI = 0; typeI < char.formsRaw.length; typeI++) {
      if (typeI * 3 + 2 >= formulaTable.length) break;
      const fbyte = char.formsRaw[typeI];
      for (const [quality, bit, qOffset] of Q_TIERS) {
        if (!(fbyte & bit)) continue;
        const lstIdx = typeI * 3 + qOffset;
        const entry = formulaTable[lstIdx];
        const key = `${formulaTypes[typeI].toLowerCase()}|${quality}`;
        const p = potionsMap.get(key);
        if (!p) { unmatched.push(`${entry.name} (q${quality})`); continue; }
        const pvalEff = p.pval + (typeI === 15 ? TRANSFORMATION_BONUS_PF : 0);
        const sr = Math.min(0.99, Math.max(0, (100 - (p.magic - total)) / 100));
        const ep = sr * pvalEff - p.cval;
        const bucket = sr > 0 ? brewable : impossible;
        bucket.push({ ep, sr, p, pvalEff });
      }
    }

    brewable.sort((a, b) => b.ep - a.ep);
    impossible.sort((a, b) => a.p.magic - b.p.magic);

    return { name: char.name, alchemy: char.alchemy, intelligence: char.intelligence, total, brewable, impossible, unmatched };
  });

  return { pstone, characters: results };
}
