import { forwardRef } from "react";
import { ArrowRight } from "lucide-react";

const cx = (...a) => a.filter(Boolean).join(" ");

/**
 * Button — primary | secondary | ghost | danger; size sm | md | lg; loading holati.
 * Hover'da 1px ko'tariladi (faqat sichqoncha), bosilganda scale(0.97) — CSS'da (.btn).
 * `as="a"` bilan havola sifatida ham ishlatiladi.
 */
export const Button = forwardRef(function Button(
  { variant = "secondary", size = "md", block = false, loading = false, icon = null, arrow = false, as: Tag = "button", className = "", disabled, children, type, ...rest },
  ref
) {
  const isButton = Tag === "button";
  return (
    <Tag
      ref={ref}
      type={isButton ? type || "button" : undefined}
      className={cx("btn", `btn-${variant}`, size !== "md" && `btn-${size}`, block && "btn-block", className)}
      disabled={isButton ? disabled || loading : undefined}
      aria-disabled={!isButton && (disabled || loading) ? true : undefined}
      aria-busy={loading || undefined}
      data-loading={loading || undefined}
      {...rest}
    >
      {loading ? <span className="spinner" aria-hidden /> : icon ? <span aria-hidden className="inline-flex">{typeof icon === "function" || icon?.render ? (() => { const I = icon; return <I size={18} strokeWidth={2} />; })() : icon}</span> : null}
      {children != null && <span>{children}</span>}
      {arrow && !loading && <ArrowRight className="arr" size={18} strokeWidth={2} aria-hidden />}
    </Tag>
  );
});

export function Spinner({ className = "" }) {
  return <span className={cx("spinner", className)} role="status" aria-label="Yuklanmoqda" />;
}
