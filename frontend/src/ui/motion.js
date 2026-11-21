// Harakat presetlari. Standart — kritik so'ndirilgan prujina (bounce 0): silliq, ortiqcha sakrashsiz.
import { useEffect, useState } from "react";

export const spring = { type: "spring", bounce: 0, duration: 0.38 };
export const springSnappy = { type: "spring", bounce: 0, duration: 0.26 };
export const springSheet = { type: "spring", bounce: 0.12, duration: 0.42 };
export const easeOut = [0.23, 1, 0.32, 1];

// Scroll'da ko'rinish: kichik siljish + shaffoflik (reduced-motion'da MotionConfig siljishni o'chiradi)
export const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: easeOut } },
};
export const stagger = (step = 0.06, delay = 0) => ({
  hidden: {},
  show: { transition: { staggerChildren: step, delayChildren: delay } },
});

export function useMediaQuery(query) {
  const get = () => (typeof window !== "undefined" && window.matchMedia ? window.matchMedia(query).matches : false);
  const [match, setMatch] = useState(get);
  useEffect(() => {
    if (!window.matchMedia) return undefined;
    const mq = window.matchMedia(query);
    const on = () => setMatch(mq.matches);
    on();
    mq.addEventListener?.("change", on);
    return () => mq.removeEventListener?.("change", on);
  }, [query]);
  return match;
}

// Sahifa scroll qilinganmi (sticky header soyasi va ixchamlashuvi uchun). rAF bilan, passive.
export function useScrolled(threshold = 8) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    let raf = 0;
    const on = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => setScrolled(window.scrollY > threshold));
    };
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => { cancelAnimationFrame(raf); window.removeEventListener("scroll", on); };
  }, [threshold]);
  return scrolled;
}
