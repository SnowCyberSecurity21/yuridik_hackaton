// Telegram Mini App: chat Huquqim hisobiga ulangan va tasdiqlangan bo'lsa — kabinet; aks holda — anonim rejim.
// Telegram mavzusiga moslashadi (colorScheme). Brauzerda ochilsa — saytga yo'naltiradi.
import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import { APP_NAME } from "./config.js";
import { AnonView, CabinetView } from "./Site.jsx";

const TG_SDK = "https://telegram.org/js/telegram-web-app.js";

function loadTelegram() {
  if (window.Telegram?.WebApp) return Promise.resolve(window.Telegram.WebApp);
  return new Promise((resolve) => {
    const timer = setTimeout(() => resolve(null), 3000);
    const s = document.createElement("script");
    s.src = TG_SDK;
    s.async = true;
    s.onload = () => { clearTimeout(timer); resolve(window.Telegram?.WebApp || null); };
    s.onerror = () => { clearTimeout(timer); resolve(null); };
    document.head.appendChild(s);
  });
}

export default function MiniApp() {
  const [wa, setWa] = useState(undefined);
  const [me, setMe] = useState(null);
  useEffect(() => {
    loadTelegram().then((w) => {
      if (w?.initData) {
        try { w.ready(); w.expand(); } catch { /* eski klient */ }
        const apply = () => document.documentElement.setAttribute("data-theme", w.colorScheme === "dark" ? "dark" : "light");
        apply();
        try { w.onEvent("themeChanged", apply); } catch { /* */ }
        setWa(w);
      } else setWa(null);
    });
  }, []);
  const headers = useMemo(() => (wa?.initData ? { "X-Telegram-Init-Data": wa.initData } : {}), [wa]);
  useEffect(() => {
    if (wa === undefined) return;
    api.get("/api/auth/me", { headers }).then((r) => setMe(r?.error ? { logged_in: false } : r));
  }, [wa, headers]);

  const site = `${window.location.origin}/kirish?next=oneid&from=tg`;
  const openSite = () => { if (wa?.openLink) wa.openLink(site); else window.location.href = site; };

  return (
    <div className="mx-auto min-h-screen max-w-md px-4 pb-10 pt-3">
      <div className="mb-3 flex items-center gap-2">
        <span className="hero-mark" style={{ width: 28, height: 28, fontSize: 12 }}>H</span>
        <span className="font-bold">{APP_NAME}</span>
        {me?.verified && <span className="badge badge-ok ml-auto">✅ {me.first_name}</span>}
      </div>
      {!me && <div className="muted py-10 text-center">Yuklanmoqda…</div>}
      {me?.verified && <CabinetView me={me} headers={headers} inMiniApp />}
      {me && !me.verified && (
        <div className="space-y-4">
          <div className="card p-4">
            <div className="font-semibold">✅ OneID bilan tasdiqlang</div>
            <p className="secondary mt-1 text-sm">Shaxsiy imtiyozlar va majburiyatlar uchun saytda hisob oching, OneID (demo) orqali tasdiqlang va «Telegram'ni ulash»ni bosing.</p>
            <button className="btn btn-primary mt-3 w-full" onClick={openSite}>Saytda tasdiqlash</button>
          </div>
          <AnonView headers={headers} compact />
        </div>
      )}
    </div>
  );
}
