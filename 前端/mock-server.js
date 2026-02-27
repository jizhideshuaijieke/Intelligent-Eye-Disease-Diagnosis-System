const http = require("http");

const PORT = 8800;
const MODEL_API_BASE = process.env.MODEL_API_BASE || "http://127.0.0.1:5000";
const MODEL_HEALTH_TIMEOUT_MS = Number(process.env.MODEL_HEALTH_TIMEOUT_MS || 800);
const MODEL_INFER_TIMEOUT_MS = Number(process.env.MODEL_INFER_TIMEOUT_MS || 30000);

const PLACEHOLDER_PNG =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/7R4AAAAASUVORK5CYII=";

const MAIN_LABELS_ZH = [
  "其他疾病",
  "糖尿病性视网膜病变",
  "病理性近视",
  "白内障",
  "老年性黄斑部病变",
  "青光眼",
  "高血压视网膜病变",
  "正常",
];

const DR_SUB_LABELS_ZH = [
  "糖网正常",
  "轻度非增殖性糖网病变",
  "中度非增殖性糖网病变",
  "重度非增殖性糖网病变",
  "增殖性糖网病变",
];

const BAR_DATA = [
  { diabetes: 2, glaucoma: 1, cataract: 0, AMD: 0, hypertension: 0, myopia: 8, others: 3 },
  { diabetes: 5, glaucoma: 2, cataract: 1, AMD: 0, hypertension: 1, myopia: 25, others: 4 },
  { diabetes: 12, glaucoma: 5, cataract: 3, AMD: 2, hypertension: 8, myopia: 35, others: 6 },
  { diabetes: 28, glaucoma: 15, cataract: 12, AMD: 8, hypertension: 22, myopia: 18, others: 9 },
  { diabetes: 45, glaucoma: 32, cataract: 38, AMD: 25, hypertension: 35, myopia: 12, others: 15 },
  { diabetes: 52, glaucoma: 48, cataract: 56, AMD: 42, hypertension: 45, myopia: 8, others: 18 },
];

function parseJsonBody(req) {
  return new Promise((resolve) => {
    let raw = "";
    req.on("data", (chunk) => {
      raw += chunk;
    });
    req.on("end", () => {
      if (!raw) {
        resolve(null);
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch {
        resolve(null);
      }
    });
    req.on("error", () => resolve(null));
  });
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function isModelAlive() {
  try {
    const res = await fetchWithTimeout(
      `${MODEL_API_BASE}/api/fundus_analysi`,
      { method: "GET" },
      MODEL_HEALTH_TIMEOUT_MS
    );
    return res.ok;
  } catch {
    return false;
  }
}

function mockProbabilities(index) {
  const base = [
    { name: "正常", probability: 0.42 },
    { name: "近视", probability: 0.18 },
    { name: "青光眼", probability: 0.12 },
    { name: "白内障", probability: 0.1 },
    { name: "糖尿病性视网膜病变", probability: 0.08 },
    { name: "老年性黄斑部病变", probability: 0.06 },
    { name: "高血压视网膜病变", probability: 0.04 },
  ];

  const offset = (Number(index) % 5) * 0.01;
  return base
    .map((item, i) => ({
      name: item.name,
      probability: Number(
        Math.max(0.01, item.probability + (i % 2 === 0 ? offset : -offset)).toFixed(3)
      ),
    }))
    .sort((a, b) => b.probability - a.probability);
}

function normalizeModelProbabilities(modelJson, index) {
  try {
    const mainRaw = modelJson?.main_classification?.probabilities || {};
    const subRaw = modelJson?.sub_classification?.probabilities || {};

    const mainValues = Object.values(mainRaw).map((v) => Number(v));
    if (mainValues.length < MAIN_LABELS_ZH.length) {
      return mockProbabilities(index);
    }

    const merged = {};
    MAIN_LABELS_ZH.forEach((label, i) => {
      merged[label] = Number((mainValues[i] || 0).toFixed(3));
    });

    const drProb = merged["糖尿病性视网膜病变"] || 0;
    if (drProb > 0.5) {
      const subValues = Object.values(subRaw)
        .map((v) => Number(v))
        .slice(0, DR_SUB_LABELS_ZH.length);
      const subSum = subValues.reduce((sum, v) => sum + (Number.isFinite(v) ? v : 0), 0) || 1;

      delete merged["糖尿病性视网膜病变"];
      DR_SUB_LABELS_ZH.forEach((label, i) => {
        const weighted = ((subValues[i] || 0) / subSum) * drProb;
        merged[label] = Number(weighted.toFixed(3));
      });
    }

    return Object.entries(merged)
      .map(([name, probability]) => ({ name, probability }))
      .sort((a, b) => b.probability - a.probability);
  } catch {
    return mockProbabilities(index);
  }
}

async function callFundusModel(imageBase64) {
  const response = await fetchWithTimeout(
    `${MODEL_API_BASE}/api/fundus_analysis`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageBase64 }),
    },
    MODEL_INFER_TIMEOUT_MS
  );

  if (!response.ok) {
    throw new Error(`fundus model failed: ${response.status}`);
  }

  return response.json();
}

async function callOctModel(imageBase64) {
  const response = await fetchWithTimeout(
    `${MODEL_API_BASE}/api/oct_segmentation`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageBase64 }),
    },
    MODEL_INFER_TIMEOUT_MS
  );

  if (!response.ok) {
    throw new Error(`oct model failed: ${response.status}`);
  }

  return response.json();
}

async function makeAiboResponse(payload) {
  const list = Array.isArray(payload) ? payload : [];
  const modelAlive = await isModelAlive();
  const data = [];

  for (const [idx, item] of list.entries()) {
    const index = Number.isFinite(Number(item?.index)) ? Number(item.index) : idx + 1;
    const name = typeof item?.name === "string" ? item.name : "";
    const sourceImage = item?.path || PLACEHOLDER_PNG;
    const isOct = name === "left-oct" || name === "right-oct";

    if (isOct) {
      let octPath = sourceImage;
      let probabilities = mockProbabilities(index);

      if (modelAlive) {
        try {
          const octJson = await callOctModel(sourceImage);
          if (octJson?.segmentation_result) {
            octPath = octJson.segmentation_result;
          }
        } catch {
          // fallback to source image
        }
      }

      data.push({
        index,
        name,
        path: octPath,
        probabilities,
      });
      continue;
    }

    let resultPath = sourceImage;
    let enhancedImage = sourceImage;
    let probabilities = mockProbabilities(index);

    if (modelAlive) {
      try {
        const fundusJson = await callFundusModel(sourceImage);
        if (fundusJson?.vessel_segmentation?.probability_map) {
          resultPath = fundusJson.vessel_segmentation.probability_map;
        }
        if (fundusJson?.enhanced_image) {
          enhancedImage = fundusJson.enhanced_image;
        }
        probabilities = normalizeModelProbabilities(fundusJson, index);
      } catch {
        // fallback to mock data
      }
    }

    data.push({
      index,
      name: name || `fundus-${index}`,
      path: resultPath,
      probabilities,
      enhanced_image: enhancedImage,
    });
  }

  return {
    code: 1,
    message: modelAlive ? "success(model)" : "success(mock)",
    data,
  };
}

function makeQuestionResponse(payload) {
  const question = payload && typeof payload.question === "string" ? payload.question.trim() : "";
  return {
    code: 1,
    message: "ok",
    data: question
      ? `根据你的问题“${question}”，建议先完善症状描述并结合眼底检查结果综合判断。`
      : "请先描述症状与既往病史，我再给你建议。",
  };
}

function makeSuggestionResponse(payload) {
  const age = payload && payload.age !== undefined ? String(payload.age) : "未知";
  const gender = payload && payload.gender !== undefined ? String(payload.gender) : "未知";
  const outcome = payload && payload.outcome !== undefined ? String(payload.outcome) : "未知";

  return {
    code: 1,
    message: "ok",
    data: `模拟临床建议\n1. 患者信息：年龄=${age}，性别=${gender}\n2. 疑似诊断：${outcome}\n3. 建议结合影像复查并动态随访。`,
  };
}

const server = http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Content-Type", "application/json; charset=utf-8");

  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end();
    return;
  }

  const payload = req.method === "POST" ? await parseJsonBody(req) : null;
  const url = req.url;
  console.log(`${req.method} ${url}`);

  let response = { code: 404, message: "Not Found", data: null };

  if (url === "/aiQuestion") {
    response = makeQuestionResponse(payload);
  } else if (url === "/aiSuggestion") {
    response = makeSuggestionResponse(payload);
  } else if (url === "/aibo") {
    response = await makeAiboResponse(payload);
  } else if (url === "/getPatientsNum") {
    response = { code: 1, message: "ok", data: [45, 52, 38, 67, 89, 76, 94, 82, 71, 63, 58, 49] };
  } else if (url === "/getDiseasesDistribution") {
    response = {
      code: 1,
      message: "ok",
      data: {
        diabetes: 35,
        glaucoma: 28,
        cataract: 22,
        AMD: 18,
        hypertension: 15,
        myopia: 42,
        others: 12,
      },
    };
  } else if (url === "/getDiseaseConditionByAge") {
    response = { code: 1, message: "ok", data: BAR_DATA };
  } else if (url === "/loginByAccount") {
    response = { code: 1, message: "ok", data: { token: "mock-token-for-demo" } };
  }

  res.writeHead(200);
  res.end(JSON.stringify(response));
});

server.listen(PORT, () => {
  console.log(`Mock server started: http://localhost:${PORT}`);
  console.log(`Model bridge target: ${MODEL_API_BASE}`);
  console.log(
    "Endpoints: /aiQuestion, /aiSuggestion, /aibo, /getPatientsNum, /getDiseasesDistribution, /getDiseaseConditionByAge, /loginByAccount"
  );
});
