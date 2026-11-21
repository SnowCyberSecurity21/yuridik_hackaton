import { forwardRef } from "react";

const cx = (...a) => a.filter(Boolean).join(" ");
const PAD = { none: "", sm: "p-3", md: "p-4 sm:p-5", lg: "p-5 sm:p-6" };

/**
 * Card — asosiy yuza. `interactive` — bosiladigan karta (hover ko'tarilish, press).
 * `inset` — ichki, soyasiz yuza (karta ichidagi blok).
 */
export const Card = forwardRef(function Card(
  { as: Tag = "div", interactive = false, inset = false, padding = "md", className = "", children, ...rest },
  ref
) {
  return (
    <Tag ref={ref} className={cx("card", inset && "card-inset", interactive && "card-interactive", PAD[padding], className)} {...rest}>
      {children}
    </Tag>
  );
});

export function CardHeader({ title, subtitle, right, as: H = "h2" }) {
  return (
    <div className="mb-4 flex flex-wrap items-start gap-3">
      <div className="min-w-0 flex-1">
        <H className="h3">{title}</H>
        {subtitle && <p className="muted small mt-0.5">{subtitle}</p>}
      </div>
      {right && <div className="flex w-full flex-wrap items-center gap-2 sm:ml-auto sm:w-auto">{right}</div>}
    </div>
  );
}
