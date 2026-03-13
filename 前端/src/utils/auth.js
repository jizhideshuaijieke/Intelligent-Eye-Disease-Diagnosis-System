const TOKEN_KEY = 'eye_diagnosis_token';
const USER_KEY = 'eye_diagnosis_user';

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

export function getAuthUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || '{}');
  } catch {
    return {};
  }
}

export function saveAuthSession(payload) {
  localStorage.setItem(TOKEN_KEY, String(payload?.token || ''));
  localStorage.setItem(
    USER_KEY,
    JSON.stringify({
      accountId: payload?.accountId || null,
      name: payload?.name || '',
    })
  );
}

export function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
