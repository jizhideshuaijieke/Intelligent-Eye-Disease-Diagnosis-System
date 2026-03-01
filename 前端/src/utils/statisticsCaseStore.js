const STORAGE_KEY = 'eye_diagnosis_exported_cases_v1';
const PENDING_KEY = 'eye_diagnosis_pending_case_v1';
export const STATS_UPDATED_EVENT = 'eye-diagnosis-stats-updated';

export const DISEASE_KEY_ORDER = [
  'diabetes',
  'glaucoma',
  'cataract',
  'AMD',
  'hypertension',
  'myopia',
  'others',
];

export const DISEASE_LABEL_MAP = {
  diabetes: '糖尿病',
  glaucoma: '青光眼',
  cataract: '白内障',
  AMD: 'AMD',
  hypertension: '高血压',
  myopia: '近视',
  others: '其他疾病或异常',
};

const DISEASE_ALIASES = {
  diabetes: [
    '糖尿病性视网膜病变',
    '糖网正常',
    '轻度非增殖性糖网病变',
    '中度非增殖性糖网病变',
    '重度非增殖性糖网病变',
    '增殖性糖网病变',
  ],
  glaucoma: ['青光眼'],
  cataract: ['白内障'],
  AMD: ['AMD', '老年性黄斑部病变', '黄斑病变'],
  hypertension: ['高血压视网膜病变', '高血压'],
  myopia: ['病理性近视', '近视性黄斑病变', '近视性视网膜病变', '近视'],
  others: ['其他疾病', '其他疾病或异常'],
};

function createDiseaseCounter() {
  return {
    diabetes: 0,
    glaucoma: 0,
    cataract: 0,
    AMD: 0,
    hypertension: 0,
    myopia: 0,
    others: 0,
  };
}

function safeParse(raw, fallback) {
  try {
    const parsed = JSON.parse(raw);
    return parsed == null ? fallback : parsed;
  } catch {
    return fallback;
  }
}

function normalizeText(text) {
  return String(text || '').replace(/\s+/g, '').trim();
}

export function mapDiagnosisNameToKey(name) {
  const normalized = normalizeText(name);
  if (!normalized || normalized === '正常') {
    return null;
  }

  for (const [key, aliases] of Object.entries(DISEASE_ALIASES)) {
    if (aliases.some((alias) => normalized.includes(alias))) {
      return key;
    }
  }

  return null;
}

export function getAgeGroupIndex(age) {
  const n = Number(age);
  if (!Number.isFinite(n) || n < 0) return null;
  if (n <= 9) return 0;
  if (n <= 19) return 1;
  if (n <= 34) return 2;
  if (n <= 49) return 3;
  if (n <= 64) return 4;
  return 5;
}

export function collectTopDiagnosisFromResults(imageResults) {
  if (!Array.isArray(imageResults)) return null;

  let best = null;
  imageResults.forEach((image) => {
    const probs = Array.isArray(image?.probabilities) ? image.probabilities : [];
    probs.forEach((item) => {
      const key = mapDiagnosisNameToKey(item?.name);
      const prob = Number(item?.probability || 0);
      if (!key || !Number.isFinite(prob)) return;
      if (!best || prob > best.probability) {
        best = {
          name: item.name,
          probability: prob,
          diseaseKey: key,
        };
      }
    });
  });

  return best;
}

export function savePendingCaseMeta(meta) {
  if (typeof window === 'undefined') return;
  const payload = {
    topDiagnosisName: String(meta?.topDiagnosisName || ''),
    topDiagnosisProbability: Number(meta?.topDiagnosisProbability || 0),
    annotationCount: Number(meta?.annotationCount || 0),
    createdAt: Date.now(),
  };
  sessionStorage.setItem(PENDING_KEY, JSON.stringify(payload));
}

export function getPendingCaseMeta() {
  if (typeof window === 'undefined') return null;
  const raw = sessionStorage.getItem(PENDING_KEY);
  return safeParse(raw, null);
}

export function clearPendingCaseMeta() {
  if (typeof window === 'undefined') return;
  sessionStorage.removeItem(PENDING_KEY);
}

export function readExportedCases() {
  if (typeof window === 'undefined') return [];
  const raw = localStorage.getItem(STORAGE_KEY);
  const parsed = safeParse(raw, []);
  return Array.isArray(parsed) ? parsed : [];
}

function writeExportedCases(cases) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cases));
  window.dispatchEvent(new CustomEvent(STATS_UPDATED_EVENT));
}

export function recordExportedCase(payload) {
  const diagnosisName = String(payload?.diagnosisName || '');
  const diagnosisKey = mapDiagnosisNameToKey(diagnosisName);
  const age = Number(payload?.age);
  const ageGroupIndex = getAgeGroupIndex(age);
  const monthIndex = Number.isFinite(Number(payload?.monthIndex)) ? Number(payload.monthIndex) : new Date().getMonth();
  const annotationCount = Number(payload?.annotationCount || 0);
  const caseId = String(payload?.caseId || '').trim();

  if (!diagnosisKey) {
    return { ok: false, message: '未识别到可统计的疾病结果（正常结果不纳入统计）。' };
  }
  if (!Number.isFinite(age) || age < 1 || age > 120 || ageGroupIndex == null) {
    return { ok: false, message: '年龄无效，未写入统计。' };
  }
  if (annotationCount <= 0) {
    return { ok: false, message: '请先完成病灶标注后再导出并入统计。' };
  }

  const cases = readExportedCases();
  if (caseId && cases.some((item) => String(item.caseId || '') === caseId)) {
    return { ok: false, message: '该病例已计入统计，已阻止重复累计。' };
  }

  const record = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    caseId,
    diagnosisName,
    diagnosisKey,
    age,
    ageGroupIndex,
    monthIndex: Math.max(0, Math.min(11, monthIndex)),
    annotationCount,
    exportedAt: new Date().toISOString(),
  };

  cases.push(record);
  writeExportedCases(cases);
  return { ok: true, record };
}

export function buildStatisticsIncrement(cases) {
  const list = Array.isArray(cases) ? cases : [];
  const monthly = new Array(12).fill(0);
  const disease = createDiseaseCounter();
  const ageDisease = Array.from({ length: 6 }, () => createDiseaseCounter());

  list.forEach((item) => {
    const monthIndex = Number(item?.monthIndex);
    const ageGroupIndex = Number(item?.ageGroupIndex);
    const key = item?.diagnosisKey;
    if (!DISEASE_KEY_ORDER.includes(key)) return;

    if (monthIndex >= 0 && monthIndex <= 11) monthly[monthIndex] += 1;
    disease[key] += 1;
    if (ageGroupIndex >= 0 && ageGroupIndex < ageDisease.length) {
      ageDisease[ageGroupIndex][key] += 1;
    }
  });

  return { monthly, disease, ageDisease };
}
