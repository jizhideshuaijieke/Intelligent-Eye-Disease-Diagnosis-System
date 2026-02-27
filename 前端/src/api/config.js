// API configuration with auto-fallback:
// 1) try REAL_API first, 2) fallback to MOCK_API.
const REAL_API = process.env.VUE_APP_REAL_API || 'http://127.0.0.1:8800';
const MOCK_API = process.env.VUE_APP_MOCK_API || 'http://127.0.0.1:8800';
const HEALTH_PATH = process.env.VUE_APP_API_HEALTH_PATH || '/getPatientsNum';
const DETECT_TIMEOUT_MS = Number(process.env.VUE_APP_API_DETECT_TIMEOUT_MS || 1000);

let apiBaseUrl = MOCK_API;

export async function initApiConfig() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DETECT_TIMEOUT_MS);
  try {
    await fetch(`${REAL_API}${HEALTH_PATH}`, { signal: controller.signal });
    apiBaseUrl = REAL_API;
    console.log('使用真实后端:', REAL_API);
  } catch {
    apiBaseUrl = MOCK_API;
    console.log('使用Mock后端:', MOCK_API);
  } finally {
    clearTimeout(timer);
  }
}

export function getApiUrl(path) {
  return `${apiBaseUrl}${path}`;
}
