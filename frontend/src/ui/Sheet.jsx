import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion, useDragControls, useReducedMotion } from "motion/react";
import { springSheet, useMediaQuery } from "./motion.js";
import { useTelegramBackButton } from "./telegram.js";

/**
 * Sheet — mobil: pastdan chiqadigan panel (tortib yopiladi); ≥640px: markazdagi modal.
 * variant="sheet" (standart, desktop'da markazga o'tadi) | "bottom" (har doim pastda).
 * Esc, fon bosilishi, Telegram BackButton — yopadi. Fokus panelga o'tadi va yopilganda qaytadi.
 */
export function Sheet({ open, onClose, title, description, footer, children, variant = "sheet", labelledBy }) {
  const wide = useMediaQuery("(min-width: 640px)");
  const center = variant !== "bottom" && wide;
  const reduce = useReducedMotion();
  const panelRef = useRef(null);
  const lastFocus = useRef(null);
  const drag = useDragControls();
  const tid = useId();
  const closeRef = useRef(onClose);
  closeRef.current = onClose;

  useTelegramBackButton(open, () => closeRef.current?.());

  useEffect(() => {
    if (!open) return undefined;
    lastFocus.current = document.activeElement;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e) => { if (e.key === "Escape") closeRef.current?.(); };
    window.addEventListener("keydown", onKey);
    const t = setTimeout(() => panelRef.current?.focus(), 30);
    return () => {
      clearTimeout(t);
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
      lastFocus.current?.focus?.();
    };
  }, [open]);

  const hidden = center
    ? { opacity: 0, scale: reduce ? 1 : 0.96, y: reduce ? 0 : 8 }
    : { y: reduce ? 0 : "100%", opacity: reduce ? 0 : 1 };
  const shown = center ? { opacity: 1, scale: 1, y: 0 } : { y: 0, opacity: 1 };

  return createPortal(
    <AnimatePresence>
      {open && (
        <>
          <motion.div key="scrim" className="sheet-scrim" onClick={onClose}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: { duration: 0.18 } }}
            transition={{ duration: 0.24 }} />
          <div key="wrap" className={`sheet-wrap ${center ? "is-center" : ""}`}>
            <motion.div
              ref={panelRef}
              className="sheet"
              role="dialog"
              aria-modal="true"
              aria-labelledby={labelledBy || (title ? tid : undefined)}
              tabIndex={-1}
              initial={hidden}
              animate={shown}
              exit={{ ...hidden, transition: { duration: 0.2, ease: [0.32, 0.72, 0, 1] } }}
              transition={center ? { duration: 0.24, ease: [0.23, 1, 0.32, 1] } : springSheet}
              drag={center || reduce ? false : "y"}
              dragControls={drag}
              dragListener={false}
              dragConstraints={{ top: 0, bottom: 0 }}
              dragElastic={{ top: 0.04, bottom: 0.9 }}
              onDragEnd={(_, info) => { if (info.offset.y > 110 || info.velocity.y > 600) onClose?.(); }}
              style={{ outline: "none" }}
            >
              {!center && (
                <div className="flex-none cursor-grab touch-none pb-1" onPointerDown={(e) => drag.start(e)} aria-hidden>
                  <div className="sheet-grip" />
                </div>
              )}
              {(title || description) && (
                <div className="sheet-head" onPointerDown={center ? undefined : (e) => drag.start(e)}>
                  <div className="min-w-0 flex-1">
                    {title && <h2 id={tid} className="h3">{title}</h2>}
                    {description && <p className="muted small mt-0.5">{description}</p>}
                  </div>
                  <button type="button" className="btn btn-ghost btn-sm -mr-2" onClick={onClose} aria-label="Yopish">✕</button>
                </div>
              )}
              <div className="sheet-body">{children}</div>
              {footer && <div className="sheet-foot">{footer}</div>}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>,
    document.body
  );
}

/** Modal — har doim markazda (≥640px), mobilda pastdan. */
export function Modal(props) {
  return <Sheet {...props} variant="sheet" />;
}
