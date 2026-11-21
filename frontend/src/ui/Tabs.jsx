import { useId, useRef, useEffect } from "react";
import { motion } from "motion/react";
import { springSnappy } from "./motion.js";

/**
 * Tabs — segment/yorliqlar. Faol fon (pill) yorliqlar orasida layout animatsiya bilan siljiydi.
 * items: [{ id, label, icon?, count? }] — istalgan sonda; gorizontalda scroll bo'ladi.
 * orientation: "horizontal" | "vertical" (kabinet yon menyusi).
 * Klaviatura: ←/→ (yoki ↑/↓), Home/End.
 */
export function Tabs({ items, value, onChange, orientation = "horizontal", ariaLabel, className = "", idPrefix }) {
  const uid = useId();
  const group = idPrefix || uid;
  const listRef = useRef(null);
  const vertical = orientation === "vertical";

  useEffect(() => {
    if (vertical) return;
    const el = listRef.current?.querySelector('[aria-selected="true"]');
    el?.scrollIntoView?.({ block: "nearest", inline: "nearest", behavior: "smooth" });
  }, [value, vertical]);

  const onKey = (e) => {
    const keys = vertical ? ["ArrowUp", "ArrowDown"] : ["ArrowLeft", "ArrowRight"];
    const i = items.findIndex((t) => t.id === value);
    let next = null;
    if (e.key === keys[0]) next = (i - 1 + items.length) % items.length;
    else if (e.key === keys[1]) next = (i + 1) % items.length;
    else if (e.key === "Home") next = 0;
    else if (e.key === "End") next = items.length - 1;
    if (next == null) return;
    e.preventDefault();
    onChange(items[next].id);
    listRef.current?.querySelectorAll('[role="tab"]')[next]?.focus();
  };

  return (
    <div ref={listRef} role="tablist" aria-label={ariaLabel} aria-orientation={orientation}
      className={`seg ${vertical ? "seg-vertical" : ""} ${className}`} onKeyDown={onKey}>
      {items.map((t) => {
        const active = t.id === value;
        return (
          <button key={t.id} type="button" role="tab" id={`${group}-tab-${t.id}`} aria-selected={active}
            tabIndex={active ? 0 : -1}
            className="seg-item" onClick={() => onChange(t.id)}>
            {active && <motion.span layoutId={`${group}-pill`} className="seg-pill" transition={springSnappy} />}
            <span className="seg-label">
              {t.icon && <span aria-hidden className="inline-flex">{typeof t.icon === "string" ? t.icon : (() => { const I = t.icon; return <I size={17} strokeWidth={2} />; })()}</span>}
              <span>{t.label}</span>
              {t.count != null && <span className="seg-count">{t.count}</span>}
            </span>
          </button>
        );
      })}
    </div>
  );
}

/** Yorliq paneli: almashganda yengil crossfade. */
export function TabPanel({ id, children, className = "" }) {
  return (
    <motion.div key={id} role="tabpanel" className={className}
      initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22, ease: [0.23, 1, 0.32, 1] }}>
      {children}
    </motion.div>
  );
}
