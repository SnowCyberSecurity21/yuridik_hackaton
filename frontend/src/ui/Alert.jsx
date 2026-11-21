const ICON = { info: "ℹ️", ok: "✅", warn: "⚠️", danger: "⛔" };

/** Alert — tone: info | ok | warn | danger. Xato/ogohlantirish — role="alert", qolgani — "status". */
export function Alert({ tone = "info", title, icon, className = "", children, action }) {
  const urgent = tone === "danger" || tone === "warn";
  return (
    <div className={`alert alert-${tone} ${className}`} role={urgent ? "alert" : "status"}>
      <span aria-hidden className="leading-6">{icon ?? ICON[tone]}</span>
      <div className="min-w-0 flex-1">
        {title && <div className="font-semibold">{title}</div>}
        {children && <div className={title ? "mt-0.5" : ""}>{children}</div>}
      </div>
      {action && <div className="flex-none">{action}</div>}
    </div>
  );
}
