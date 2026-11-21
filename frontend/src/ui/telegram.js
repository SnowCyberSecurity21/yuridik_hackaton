// Telegram WebApp yordamchilari. Telegram'dan tashqarida (oddiy brauzer) hammasi jimgina no-op.
import { useEffect, useRef } from "react";

export function getWebApp() {
  const wa = typeof window !== "undefined" ? window.Telegram?.WebApp : null;
  return wa && wa.initData ? wa : null;
}

export function haptic(kind = "light") {
  try {
    const h = getWebApp()?.HapticFeedback;
    if (!h) return;
    if (kind === "success" || kind === "error" || kind === "warning") h.notificationOccurred(kind);
    else if (kind === "select") h.selectionChanged();
    else h.impactOccurred(kind);
  } catch { /* eski klient */ }
}

// Telegram mavzusi → dizayn tokenlari. Brend rangi (lojuvard) o'zgarmaydi, sirt va matn Telegram'ga moslashadi.
export function applyTelegramTheme(wa) {
  if (!wa) return;
  const root = document.documentElement;
  root.setAttribute("data-theme", wa.colorScheme === "dark" ? "dark" : "light");
  const p = wa.themeParams || {};
  const map = {
    "--bg": p.secondary_bg_color || p.bg_color,
    "--surface-1": p.section_bg_color || p.bg_color,
    "--text-primary": p.text_color,
    "--text-muted": p.hint_color,
    "--text-secondary": p.subtitle_text_color,
  };
  for (const [k, v] of Object.entries(map)) {
    if (v) root.style.setProperty(k, v); else root.style.removeProperty(k);
  }
  try {
    wa.setHeaderColor?.("secondary_bg_color");
    wa.setBackgroundColor?.("secondary_bg_color");
  } catch { /* eski klient */ }
}

// Har bir bosishda yengil haptik (tugma, yorliq, chip, havola)
export function installTapHaptics() {
  const wa = getWebApp();
  if (!wa) return () => {};
  const onDown = (e) => {
    const el = e.target.closest?.("button, a, [role='tab'], .chip, .card-interactive");
    if (el && !el.disabled) haptic("light");
  };
  document.addEventListener("pointerdown", onDown, { passive: true });
  return () => document.removeEventListener("pointerdown", onDown);
}

// Telegram BackButton: faol bo'lsa ko'rinadi va onBack chaqiradi. Eng oxirgi faol chaqiruvchi ustun.
const backStack = [];
function syncBack() {
  const wa = getWebApp();
  if (!wa?.BackButton) return;
  if (backStack.length) wa.BackButton.show(); else wa.BackButton.hide();
}
let backBound = false;
function bindBack() {
  const wa = getWebApp();
  if (backBound || !wa?.BackButton) return;
  backBound = true;
  wa.BackButton.onClick(() => { const top = backStack[backStack.length - 1]; top?.current?.(); });
}

export function useTelegramBackButton(active, onBack) {
  const ref = useRef(onBack);
  ref.current = onBack;
  useEffect(() => {
    if (!active || !getWebApp()) return undefined;
    bindBack();
    backStack.push(ref);
    syncBack();
    return () => {
      const i = backStack.lastIndexOf(ref);
      if (i >= 0) backStack.splice(i, 1);
      syncBack();
    };
  }, [active]);
}

// Telegram MainButton: pastdagi katta tugma. Brauzerda hech narsa qilmaydi (sahifadagi oddiy tugma ishlaydi).
export function useTelegramMainButton({ text, onClick, active = true, loading = false }) {
  const ref = useRef(onClick);
  ref.current = onClick;
  useEffect(() => {
    const mb = getWebApp()?.MainButton;
    if (!mb || !active) return undefined;
    const handler = () => { haptic("medium"); ref.current?.(); };
    try {
      mb.setText(text);
      mb.onClick(handler);
      mb.show();
    } catch { /* */ }
    return () => {
      try { mb.offClick(handler); mb.hide(); } catch { /* */ }
    };
  }, [text, active]);
  useEffect(() => {
    const mb = getWebApp()?.MainButton;
    if (!mb || !active) return;
    try { if (loading) mb.showProgress(false); else mb.hideProgress(); } catch { /* */ }
  }, [loading, active]);
}

export const inTelegram = () => !!getWebApp();
