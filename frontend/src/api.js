// Backend API klienti. Har bir so'rovda timeout; xatoda {error} qaytadi (UI qulamaydi).
const TIMEOUT_MS = 30000;

function adminHeaders() {
  const t = localStorageSafe("adminToken");
  return t ? { "X-Admin-Token": t } : {};
}

export function localStorageSafe(key, value) {
  try {
    if (value === undefined) return window.localStorage.getItem(key);
    window.localStorage.setItem(key, value);
    return value;
  } catch {
    return null;
  }
}

async function request(path, options = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(path, {
      ...options,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...adminHeaders(), ...(options.headers || {}) },
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) return { error: data?.detail || `Xato ${res.status}` };
    return data;
  } catch (e) {
    return { error: e.name === "AbortError" ? "Server javob bermadi (timeout)" : "Server bilan aloqa yo'q" };
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  get: (p, opts = {}) => request(p, opts),
  post: (p, body, opts = {}) => request(p, { ...opts, method: "POST", body: JSON.stringify(body ?? {}) }),
};
