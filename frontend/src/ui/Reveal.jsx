// Scroll'da paydo bo'lish, raqamlar count-up, sahifa o'tishi. Faqat transform + opacity.
import { useEffect, useRef } from "react";
import { animate, motion, useInView, useReducedMotion } from "motion/react";
import { easeOut, fadeUp, stagger } from "./motion.js";

/** Bitta blok: ko'rinish maydoniga kirganda fade + slide-up (bir marta). */
export function Reveal({ as = "div", delay = 0, className = "", children, ...rest }) {
  const M = motion[as] || motion.div;
  return (
    <M className={className} initial="hidden" whileInView="show" viewport={{ once: true, margin: "0px 0px -60px 0px" }}
      variants={{ hidden: fadeUp.hidden, show: { ...fadeUp.show, transition: { ...fadeUp.show.transition, delay } } }} {...rest}>
      {children}
    </M>
  );
}

/** Guruh: ichidagi <RevealItem> lar navbat bilan (stagger) chiqadi. */
export function RevealGroup({ as = "div", step = 0.07, delay = 0, className = "", children, ...rest }) {
  const M = motion[as] || motion.div;
  return (
    <M className={className} initial="hidden" whileInView="show" viewport={{ once: true, margin: "0px 0px -60px 0px" }}
      variants={stagger(step, delay)} {...rest}>
      {children}
    </M>
  );
}

export function RevealItem({ as = "div", className = "", children, ...rest }) {
  const M = motion[as] || motion.div;
  return <M className={className} variants={fadeUp} {...rest}>{children}</M>;
}

/** Raqam ko'rinishga kirganda 0 dan qiymatgacha sanaladi. Qayta render qilmaydi (textContent). */
export function CountUp({ value, format = (n) => new Intl.NumberFormat("ru-RU").format(n), duration = 1.1, className = "" }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "0px 0px -40px 0px" });
  const reduce = useReducedMotion();
  const num = typeof value === "number" && Number.isFinite(value) ? value : null;
  const decimals = num != null && !Number.isInteger(num) ? 1 : 0;

  useEffect(() => {
    const el = ref.current;
    if (!el || num == null) return undefined;
    if (!inView || reduce) { if (reduce || inView) el.textContent = format(num); return undefined; }
    const ctrl = animate(0, num, {
      duration, ease: easeOut,
      onUpdate: (v) => { el.textContent = format(decimals ? Math.round(v * 10) / 10 : Math.round(v)); },
    });
    return () => ctrl.stop();
  }, [inView, num, reduce]); // eslint-disable-line react-hooks/exhaustive-deps

  return <span ref={ref} className={`tabnum ${className}`}>{num == null ? (value ?? "—") : format(reduce ? num : 0)}</span>;
}

/** Sahifa o'tishi: yangi sahifa yengil ko'tarilib paydo bo'ladi. */
export function PageTransition({ id, children, className = "" }) {
  return (
    <motion.div key={id} className={className}
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, transition: { duration: 0.12 } }}
      transition={{ duration: 0.32, ease: easeOut }}>
      {children}
    </motion.div>
  );
}
