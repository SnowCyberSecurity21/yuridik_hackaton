// Skeleton, EmptyState, Toast — kutish, bo'shliq va tasdiq holatlari.
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "motion/react";
import { haptic } from "./telegram.js";

const cx = (...a) => a.filter(Boolean).join(" ");

/* ------------------------------------------------------------------ Skeleton */
export function Skeleton({ className = "", style }) {
  return <div className={cx("skeleton", className)} style={style} aria-hidden />;
}

/** Karta shaklidagi skeleton. lines — matn qatorlari soni. */
export function SkeletonCard({ lines = 3, className = "" }) {
  return (
    <div className={cx("card p-4 sm:p-5", className)} aria-hidden>
      <Skeleton className="h-5 w-2/3" />
      <div className="mt-3 space-y-2">
        {Array.from({ length: lines }, (_, i) => <Skeleton key={i} className="h-3.5" style={{ width: `${92 - i * 14}%` }} />)}
      </div>
    </div>
  );
}

/** Ro'yxat skeleti + ekran o'quvchilar uchun "yuklanmoqda" */
export function SkeletonList({ count = 3, lines = 3 }) {
  return (
    <div className="space-y-3" role="status" aria-label="Yuklanmoqda">
      {Array.from({ length: count }, (_, i) => <SkeletonCard key={i} lines={lines} />)}
    </div>
  );
}

/* ------------------------------------------------------------------ EmptyState */
export function EmptyState({ icon = "🗂️", title, children, action, className = "" }) {
  return (
    <div className={cx("empty", className)}>
      <span className="empty-icon" aria-hidden>{icon}</span>
      {title && <div className="font-semibold">{title}</div>}
      {children && <div className="secondary small measure">{children}</div>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

/* ------------------------------------------------------------------ Toast */
// Ishlatish: <Toaster /> ni bir marta joylang, keyin istalgan joydan toast("Nusxa olindi").
const listeners = new Set();
let seq = 0;

export function toast(message, { tone = "neutral", icon, duration = 2800 } = {}) {
  const t = { id: ++seq, message, tone, icon, duration };
  listeners.forEach((fn) => fn(t));
  haptic(tone === "danger" ? "error" : "success");
  return t.id;
}

const TONE_ICON = { ok: "✅", danger: "⚠️", warn: "⚠️", neutral: null };

export function Toaster() {
  const [items, setItems] = useState([]);
  useEffect(() => {
    const add = (t) => {
      setItems((xs) => [...xs.slice(-2), t]);
      setTimeout(() => setItems((xs) => xs.filter((x) => x.id !== t.id)), t.duration);
    };
    listeners.add(add);
    return () => listeners.delete(add);
  }, []);
  return createPortal(
    <div className="toaster" aria-live="polite" aria-atomic="false">
      <AnimatePresence initial={false}>
        {items.map((t) => (
          <motion.div key={t.id} layout className="toast" role="status"
            initial={{ opacity: 0, y: 16, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, transition: { duration: 0.16 } }}
            transition={{ type: "spring", bounce: 0, duration: 0.32 }}
            drag="y" dragConstraints={{ top: 0, bottom: 0 }} dragElastic={{ top: 0, bottom: 0.6 }}
            onDragEnd={(_, i) => { if (i.offset.y > 30 || i.velocity.y > 300) setItems((xs) => xs.filter((x) => x.id !== t.id)); }}>
            {(t.icon ?? TONE_ICON[t.tone]) && <span aria-hidden>{t.icon ?? TONE_ICON[t.tone]}</span>}
            <span>{t.message}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>,
    document.body
  );
}
