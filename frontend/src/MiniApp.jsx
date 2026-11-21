// Telegram Mini App: chat Huquqim hisobiga ulangan va tasdiqlangan bo'lsa — kabinet; aks holda — anonim rejim.
// Telegram ichida: ready/expand, themeParams → tokenlar, MainButton, BackButton, har bosishda haptik.
// Oddiy brauzerda ochilsa ham ishlaydi (Telegram tugmalari o'rniga sahifadagi tugmalar).
import { useEffect, useMemo, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { api } from "./api.js";
import { AnonView, CabinetView } from "./Site.jsx";
import {
  Badge, Button, Card, Logo, SkeletonList, applyTelegramTheme, installTapHaptics, useTelegramMainButton,
} from "./ui/index.js";

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
    let cleanup = () => {};
    loadTelegram().then((w) => {
      if (w?.initData) {
        try { w.ready(); w.expand(); } catch { /* eski klient */ }
        try { w.disableVerticalSwipes?.(); } catch { /* */ }
        const apply = () => applyTelegramTheme(w);
        apply();
        try { w.onEvent("themeChanged", apply); } catch { /* */ }
        cleanup = installTapHaptics();
        setWa(w);
      } else setWa(null);
    });
    return () => cleanup();
  }, []);
  const headers = useMemo(() => (wa?.initData ? { "X-Telegram-Init-Data": wa.initData } : {}), [wa]);
  useEffect(() => {
    if (wa === undefined) return;
    api.get("/api/auth/me", { headers }).then((r) => setMe(r?.error ? { logged_in: false } : r));
  }, [wa, headers]);

  const site = `${window.location.origin}/kirish?next=oneid&from=tg`;
  const openSite = () => { if (wa?.openLink) wa.openLink(site); else window.location.href = site; };
  const needsVerify = !!me && !me.verified;
  useTelegramMainButton({ text: "OneID bilan tasdiqlash", onClick: openSite, active: needsVerify && !!wa });

  return (
    <div className="mx-auto min-h-screen max-w-md px-4 pb-24 pt-3" style={{ paddingTop: "max(12px, env(safe-area-inset-top))" }}>
      <header className="mb-4 flex items-center gap-2">
        <Logo height={30} />
        {me?.verified && <Badge tone="verified" className="ml-auto"><ShieldCheck size={14} style={{ color: "var(--feruza)" }} /> {me.first_name}</Badge>}
        {!wa && wa !== undefined && !me?.verified && <Badge className="ml-auto">Brauzer rejimi</Badge>}
      </header>
      {!me && <SkeletonList count={3} />}
      {me?.verified && <CabinetView me={me} headers={headers} inMiniApp />}
      {needsVerify && (
        <div className="space-y-5">
          <Card padding="md">
            <div className="h3">Shaxsiy kabinet uchun OneID bilan tasdiqlang</div>
            <p className="secondary mt-1 text-sm">Saytda hisob oching, OneID (demo) orqali tasdiqlang va «Telegram'ni ulash» ni bosing. Imtiyozlar va muddatlar shu yerda ochiladi.</p>
            {!wa && <Button variant="primary" block arrow className="mt-4" onClick={openSite}>Saytda tasdiqlash</Button>}
          </Card>
          <AnonView headers={headers} compact />
        </div>
      )}
    </div>
  );
}
