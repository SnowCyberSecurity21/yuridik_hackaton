// RightsCategories — «Mening huquqlarim»: Talaba, Bolali ona, Yuridik shaxs / tadbirkor, Pensioner, Haydovchi.
// Har yozuv ochilganda — lex.uz'dagi asl abzas va oddiy til (LawView). Natija hech qachon «albatta» emas.
import { useEffect, useId, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Alert, Badge, Button, EmptyState, SkeletonList, Tabs, spring } from "../ui";
import { featuresApi } from "./api.js";
import LawView from "./LawView.jsx";

const SECTIONS = [
  { key: "benefits", title: "Imtiyozlar", note: "Haqli bo'lishingiz mumkin — shartlarni tekshiring" },
  { key: "rights", title: "Huquqlar" },
  { key: "duties", title: "Majburiyatlar" },
  { key: "documents", title: "Kerakli hujjatlar" },
];

function Item({ item, kind, onAppeal }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  return (
    <li className="card card-inset p-0">
      <button type="button" className="flex w-full items-start gap-3 p-4 text-left" aria-expanded={open}
        aria-controls={panelId} onClick={() => setOpen((v) => !v)}>
        <span className="min-w-0 flex-1">
          <span className="block font-semibold" style={{ color: "var(--text-primary)" }}>{item.title}</span>
          <span className="secondary small mt-1 block">{item.plain}</span>
        </span>
        <motion.span aria-hidden className="muted mt-0.5 shrink-0 text-lg leading-none"
          animate={{ rotate: open ? 45 : 0 }} transition={spring}>+</motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div id={panelId} key="body" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={spring} style={{ overflow: "hidden" }}>
            <div className="grid gap-3 px-4 pb-4">
              {kind === "benefits" && item.conditions?.length > 0 && (
                <div>
                  <p className="small font-semibold">Tekshirilishi kerak bo'lgan shartlar</p>
                  <ul className="small secondary mt-1 list-disc pl-5">
                    {item.conditions.map((c) => <li key={c}>{c}</li>)}
                  </ul>
                </div>
              )}
              <LawView excerpts={item.excerpts} compact />
              {kind === "benefits" && onAppeal && (
                <div>
                  <Button size="sm" variant="primary" icon="📝" onClick={() => onAppeal(item)}>Ariza tayyorlash</Button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </li>
  );
}

function CategoryBody({ v, onAppeal }) {
  return (
    <div className="grid gap-6">
      {v.intro && <p className="lead">{v.intro}</p>}

      {SECTIONS.map(({ key, title, note }) => v[key]?.length > 0 && (
        <section key={key} aria-label={title}>
          <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h3 className="h2">{title}</h3>
            {note && <span className="small muted">{note}</span>}
          </div>
          <ul className="grid gap-2">
            {v[key].map((it) => <Item key={it.id} item={it} kind={key} onAppeal={onAppeal} />)}
          </ul>
        </section>
      ))}

      {v.where_to_go?.length > 0 && (
        <section aria-label="Qayerga borish">
          <h3 className="h2 mb-3">Qayerga borish</h3>
          <ul className="grid gap-2 sm:grid-cols-2">
            {v.where_to_go.map((w) => (
              <li key={w.name}>
                <a className="card card-interactive block p-3" href={w.url} target="_blank" rel="noopener noreferrer">
                  <span className="block font-semibold small" style={{ color: "var(--text-primary)" }}>{w.name}</span>
                  <span className="tiny muted">{w.url.replace(/^https:\/\//, "")}</span>
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-label="Yangiliklar">
        <h3 className="h2 mb-3">Yangiliklar</h3>
        {v.news?.length ? (
          <ul className="grid gap-2">
            {v.news.map((n) => (
              <li key={n.id} className="card p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="small tabnum muted">{n.date_text}</span>
                  {n.is_demo ? <Badge tone="unverified">DEMO o'zgarish</Badge> : <Badge tone="source">lex.uz</Badge>}
                </div>
                <p className="mt-1 font-semibold" style={{ color: "var(--text-primary)" }}>{n.title}</p>
                {n.plain && <p className="secondary small mt-1">{n.plain}</p>}
                {n.excerpts?.length > 0 && <div className="mt-3"><LawView excerpts={n.excerpts} compact /></div>}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted small">Hozircha yangilik yo'q. Sizga taalluqli qonun o'zgarsa, shu yerda ko'rasiz.</p>
        )}
      </section>

      <p className="source">{v.disclaimer}</p>
    </div>
  );
}

/**
 * Props:
 *   initial   — boshlang'ich toifa id (student | mother | entrepreneur | pensioner | driver)
 *   only      — faqat shu toifalar (masalan, kabinetda shaxsning toifalari)
 *   onAppeal  — (item) => void; imtiyoz uchun «Ariza tayyorlash» tugmasi (berilmasa — tugma yo'q)
 *   lang      — "uz" | "ru"
 */
export default function RightsCategories({ initial, only, onAppeal, lang = "uz" }) {
  const [cats, setCats] = useState(null);
  const [active, setActive] = useState(initial || null);
  const [view, setView] = useState({ loading: false, data: null, error: null });

  useEffect(() => {
    featuresApi.categories(lang).then((r) => {
      if (r.error) return setCats({ error: r.error });
      const list = only?.length ? r.categories.filter((c) => only.includes(c.id)) : r.categories;
      setCats({ list });
      setActive((a) => a && list.some((c) => c.id === a) ? a : list[0]?.id || null);
    });
  }, [lang, only?.join(",")]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active) return undefined;
    let alive = true;
    setView((s) => ({ ...s, loading: true, error: null }));
    featuresApi.category(active, lang).then((r) => {
      if (alive) setView(r.error ? { loading: false, data: null, error: r.error } : { loading: false, data: r, error: null });
    });
    return () => { alive = false; };
  }, [active, lang]);

  if (!cats) return <SkeletonList count={3} />;
  if (cats.error) return <Alert tone="warn" title="Toifalarni yuklab bo'lmadi">{cats.error}</Alert>;
  if (!cats.list.length) return <EmptyState title="Toifa topilmadi">Profilingizga mos toifa hozircha yo'q.</EmptyState>;

  return (
    <div className="grid gap-5">
      <Tabs ariaLabel="Toifalar" value={active} onChange={setActive}
        items={cats.list.map((c) => ({ id: c.id, label: c.title, icon: c.icon }))} />
      {view.loading && !view.data && <SkeletonList count={3} />}
      {view.error && <Alert tone="warn" title="Ma'lumotni yuklab bo'lmadi">{view.error}</Alert>}
      {view.data && (
        <motion.div key={view.data.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.18 }}
          aria-busy={view.loading || undefined}>
          <CategoryBody v={view.data} onAppeal={onAppeal} />
        </motion.div>
      )}
    </div>
  );
}
