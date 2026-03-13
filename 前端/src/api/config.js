const API_BASE = process.env.VUE_APP_API_BASE || process.env.VUE_APP_REAL_API || 'http://127.0.0.1:8800';
const HEALTH_PATH = process.env.VUE_APP_API_HEALTH_PATH || '/health';
const DETECT_TIMEOUT_MS = Number(process.env.VUE_APP_API_DETECT_TIMEOUT_MS || 1000);

let apiBaseUrl = API_BASE;

export async function initApiConfig() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DETECT_TIMEOUT_MS);

  try {
    await fetch(`${API_BASE}${HEALTH_PATH}`, { signal: controller.signal });
    console.log('Using backend API:', API_BASE);
  } catch (error) {
    console.warn('Backend API is not reachable during bootstrap:', API_BASE, error);
  } finally {
    clearTimeout(timer);
  }

  apiBaseUrl = API_BASE;
}

export function getApiUrl(path) {
  return `${apiBaseUrl}${path}`;
}
