// Umumiy UI bo'laklari
export const REGION_NAMES = {};

export function fmt(n) {
  if (n === null || n === undefined) return "—";
  return new Intl.NumberFormat("ru-RU").format(n);
}

export function Wow({ pct }) {
  if (pct === null || pct === undefined) return <span className="muted">—</span>;
  const up = pct >= 0;
  return (
    <span className="tabnum secondary" title="O'tgan haftaga nisbatan">
      {up ? "▲" : "▼"} {Math.abs(pct)}%
    </span>
  );
}

export function StatusBadge({ verified, reverify, sourceChecked }) {
  if (reverify) return <span className="badge badge-crit">🔄 Qayta tekshirish</span>;
  if (!verified && sourceChecked) return <span className="badge badge-acc">📚 Manba tekshirildi</span>;
  if (!verified) return <span className="badge badge-warn">⚠️ Tekshirilmagan</span>;
  return <span className="badge badge-ok">✅ Tekshirilgan</span>;
}

export function Section({ title, subtitle, right, children, className = "" }) {
  return (
    <section className={`card p-5 ${className}`}>
      <div className="mb-4 flex flex-wrap items-start gap-3">
        <div className="min-w-0">
          <h2 className="text-base font-semibold">{title}</h2>
          {subtitle && <p className="muted mt-0.5 text-sm">{subtitle}</p>}
        </div>
        {right && <div className="flex w-full flex-wrap items-center gap-2 sm:ml-auto sm:w-auto">{right}</div>}
      </div>
      {children}
    </section>
  );
}

export function ErrorNote({ error }) {
  if (!error) return null;
  return <div className="badge badge-crit my-2">⚠️ {error}</div>;
}

export function DiffBlock({ oldText, newText }) {
  return (
    <div className="space-y-1 text-sm leading-relaxed">
      <div><del>{oldText}</del></div>
      <div><ins>{newText}</ins></div>
    </div>
  );
}

export function ChartTooltip({ active, payload, label, unit = "savol" }) {
  if (!active || !payload?.length) return null;
  const p = payload[0];
  return (
    <div className="card px-3 py-2 text-sm shadow-lg">
      <div className="secondary">{p.payload?.name ?? label}</div>
      <div className="tabnum font-semibold">{fmt(p.value)} {unit}</div>
      {p.payload?.topTitle && <div className="muted text-xs">Eng ko'p: {p.payload.topTitle}</div>}
    </div>
  );
}
