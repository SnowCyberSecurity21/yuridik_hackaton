import { Suspense, lazy, useCallback, useEffect, useState } from "react";
import { AnimatePresence, MotionConfig } from "motion/react";
import MiniApp from "./MiniApp.jsx";
import { api } from "./api.js";
import { APP_NAME } from "./config.js";
import { AnonView, AuthPage, CabinetPage, Footer, Header, ThemeToggle } from "./Site.jsx";
import Home from "./Home.jsx";
import { Badge, Logo, PageTransition, SkeletonList, Toaster, useScrolled } from "./ui/index.js";

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

function DashboardShell() {
  const scrolled = useScrolled();
  return (
    <div className="min-h-screen">
      <header className="site-header" data-scrolled={scrolled}>
        <div className="mx-auto flex h-[var(--header-h)] max-w-7xl items-center gap-3 px-4">
          <span className="brand"><Logo size={30} textClassName="hidden sm:inline" /></span>
          <span className="secondary hidden text-sm font-medium sm:inline">Davlat dashboardi</span>
          <div className="ml-auto flex items-center gap-2">
            <Badge tone="warn" title="Analitika soxta demo ma'lumot">Demo ma'lumot</Badge>
            <ThemeToggle />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Suspense fallback={<SkeletonList count={3} />}><Dashboard /></Suspense>
      </main>
    </div>
  );
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
  useEffect(() => { document.title = path.startsWith("/dashboard") ? `${APP_NAME} — dashboard` : APP_NAME; }, [path]);

  let content;
  if (path.startsWith("/miniapp")) content = <MiniApp />;
  else if (path.startsWith("/dashboard")) content = <DashboardShell />;
  else {
    let page;
    let key = "home";
    if (path.startsWith("/anonim")) { page = <AnonView />; key = "anon"; }
    else if (path.startsWith("/kirish")) { page = <AuthPage onAuthed={(r) => setMe(r)} />; key = "auth"; }
    else if (path.startsWith("/kabinet")) { page = <CabinetPage me={me} onReload={reload} />; key = "cabinet"; }
    else page = <Home me={me} />;
    const wide = key === "home" || key === "cabinet";
    content = (
      <div className="flex min-h-screen flex-col">
        <Header me={me} wide={wide} />
        <main className={`mx-auto w-full flex-1 px-4 pb-16 pt-4 ${wide ? "max-w-6xl" : "max-w-3xl"}`}>
          <AnimatePresence mode="wait" initial={false}>
            <PageTransition key={key} id={key}>{page}</PageTransition>
          </AnimatePresence>
        </main>
        <Footer wide={wide} />
      </div>
    );
  }

  return (
    <MotionConfig reducedMotion="user">
      {content}
      <Toaster />
    </MotionConfig>
  );
}
