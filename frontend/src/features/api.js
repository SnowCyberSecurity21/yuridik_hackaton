// features/ uchun API chaqiruvlari. Har so'rovda timeout; xatoda { error } qaytadi — UI hech qachon qulamaydi.
const TIMEOUT_MS = 25000;

async function request(path, { method = "GET", body } = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(path, {
      method,
      signal: ctrl.signal,
      credentials: "same-origin",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) return { error: data?.detail || `Xato ${res.status}` };
    return data ?? { error: "Bo'sh javob" };
  } catch (e) {
    return { error: e.name === "AbortError" ? "Server javob bermadi. Qayta urinib ko'ring." : "Server bilan aloqa yo'q." };
  } finally {
    clearTimeout(timer);
  }
}

const qs = (params) => {
  const s = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== "")).toString();
  return s ? `?${s}` : "";
};

export const featuresApi = {
  // «Mening huquqlarim» toifalari
  categories: (lang = "uz") => request(`/api/rights/categories${qs({ lang })}`),
  category: (id, lang = "uz") => request(`/api/rights/category/${encodeURIComponent(id)}${qs({ lang })}`),

  // Qonun abzaslari: { ids: [...] } | { category } | { item }
  excerpts: ({ ids, category, item, lang = "uz" } = {}) =>
    request(`/api/lex/excerpts${qs({ ids: ids?.join(","), category, item, lang })}`),

  // Savol-javob (karta / lex parchasi / topilmadi)
  ask: (text, { lang, legalStatus, region } = {}) =>
    request("/api/ask", { method: "POST", body: { text, lang, legal_status: legalStatus, region, channel: "web" } }),

  // Murojaat
  appealTemplates: () => request("/api/appeal/templates"),
  appeal: (cardId, fields = {}, lang = "uz") =>
    request("/api/appeal", { method: "POST", body: { card_id: cardId, fields, lang } }),
  cards: () => request("/api/cards"),
};
