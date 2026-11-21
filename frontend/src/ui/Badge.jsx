const cx = (...a) => a.filter(Boolean).join(" ");

/** Badge — tone: neutral | ok | warn | danger | info | verified | source | unverified */
export function Badge({ tone = "neutral", className = "", children, ...rest }) {
  return <span className={cx("badge", tone !== "neutral" && `badge-${tone}`, className)} {...rest}>{children}</span>;
}

/** Rasmiy manba huquqshunos tomonidan tekshirilgan */
export function VerifiedBadge({ children = "Tekshirilgan manba" }) {
  return <Badge tone="verified" title="Huquqshunos tasdiqlagan, rasmiy manba bilan solishtirilgan">✅ {children}</Badge>;
}

/** Manba (lex.uz) havolasi va rekvizitlari tekshirilgan, lekin mazmun hali tasdiqlanmagan */
export function SourceCheckedBadge({ children = "Manba tekshirildi" }) {
  return <Badge tone="source" title="Hujjat nomi, raqami va lex.uz havolasi tekshirilgan">📚 {children}</Badge>;
}

/** Demo mazmun — huquqshunos tekshirmagan */
export function UnverifiedBadge({ children = "TEKSHIRILMAGAN" }) {
  return <Badge tone="unverified" title="Demo mazmun: huquqshunos hali tekshirmagan">{children}</Badge>;
}

/** Holatga qarab mos badge */
export function TrustBadge({ verified, sourceChecked, reverify }) {
  if (reverify) return <Badge tone="danger">🔄 Qayta tekshirish</Badge>;
  if (verified) return <VerifiedBadge />;
  if (sourceChecked) return <SourceCheckedBadge />;
  return <UnverifiedBadge />;
}
