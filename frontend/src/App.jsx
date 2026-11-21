import { Suspense, lazy, useCallback, useEffect, useState } from "react";
import MiniApp from "./MiniApp.jsx";
import { api } from "./api.js";
import { APP_NAME } from "./config.js";
import { AnonView, AuthPage, CabinetPage, Header, Home, ThemeToggle, go } from "./Site.jsx";

// Davlat dashboardi (Recharts) alohida yuklanadi; /dashboard nginx basic auth ortida.
const Dashboard = lazy(() => import("./Dashboard.jsx"));

function useMe() {
  const [me, setMe] = useState(null);
  const reload = useCallback(async () => {
    const r = await api.get("/api/auth/me");
    setMe(r?.error ? { logged_in: false } : r);
  }, []);
  useEffect(() => { reload(); }, [reload]);
  return [me, reload, setMe];
}

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [me, reload, setMe] = useMe();
  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  useEffect(() => { window.scrollTo(0, 0); }, [path]);

  if (path.startsWith("/miniapp")) return <MiniApp />;

  if (path.startsWith("/dashboard")) {
    return (
      <div className="min-h-screen">
        <header className="sticky top-0 z-10 border-b" style={{ background: "var(--surface-1)", borderColor: "var(--border)" }}>
          <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-4 py-3">
            <span className="hero-mark" style={{ width: 32, height: 32, fontSize: 14 }}>H</span>
            <span className="text-lg font-bold">{APP_NAME} — davlat dashboardi</span>
            <div className="ml-auto flex items-center gap-2">
              <span className="badge badge-warn" title="Analitika soxta demo ma'lumot">⚠️ DEMO ma'lumot</span>
              <ThemeToggle />
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">
          <Suspense fallback={<div className="muted py-10 text-center">Yuklanmoqda…</div>}><Dashboard /></Suspense>
        </main>
      </div>
    );
  }

  let page;
  if (path.startsWith("/anonim")) page = <AnonView />;
  else if (path.startsWith("/kirish")) page = <AuthPage onAuthed={(r) => setMe(r)} />;
  else if (path.startsWith("/kabinet")) page = <CabinetPage me={me} onReload={reload} />;
  else page = <Home me={me} />;

  return (
    <div className="min-h-screen">
      <Header me={me} />
      <main className="mx-auto max-w-3xl px-4 pb-16 pt-4">{page}</main>
      <footer className="mx-auto max-w-3xl px-4 pb-8 text-xs muted">
        {APP_NAME} · Demo · <a className="underline" href="/" onClick={(e) => { e.preventDefault(); go("/"); }}>Bosh sahifa</a> · Manbalar: lex.uz
      </footer>
    </div>
  );
}
