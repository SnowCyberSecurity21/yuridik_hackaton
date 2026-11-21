// Huquqim UI — yagona komponentlar to'plami. Faqat dizayn tokenlaridan foydalanadi (src/index.css).
//
//   import { Button, Card, Badge, Alert, Tabs, Sheet, Skeleton, EmptyState, toast } from "../ui";
//
// Tugma:      <Button variant="primary|secondary|ghost|danger" size="sm|md|lg" loading block icon="📝">…</Button>
// Karta:      <Card interactive inset padding="sm|md|lg" as="section">…</Card>, <CardHeader title subtitle right />
// Belgi:      <Badge tone="ok|warn|danger|info|verified|source|unverified" />,
//             <VerifiedBadge /> «✅ Tekshirilgan manba», <SourceCheckedBadge /> «📚 Manba tekshirildi»,
//             <UnverifiedBadge /> «TEKSHIRILMAGAN», <TrustBadge verified sourceChecked reverify />
// Xabar:      <Alert tone="info|ok|warn|danger" title action>…</Alert>
// Yorliqlar:  <Tabs items={[{id,label,icon,count}]} value onChange orientation="horizontal|vertical" /> + <TabPanel id>
// Panel:      <Sheet open onClose title description footer>…</Sheet> (mobil — pastdan, desktop — modal)
// Kutish:     <Skeleton className="h-4 w-1/2" />, <SkeletonCard lines />, <SkeletonList count />
// Bo'shliq:   <EmptyState icon title action>…</EmptyState>
// Toast:      <Toaster /> (App'da bir marta), keyin toast("Nusxa olindi", { tone: "ok" })
// Harakat:    <Reveal>, <RevealGroup><RevealItem/></RevealGroup>, <CountUp value={557254} />, <PageTransition id>
// Telegram:   haptic("light"), useTelegramMainButton({text,onClick,active}), useTelegramBackButton(active, onBack)
// Matn klasslari: .display .h1 .h2 .h3 .lead .law (qonun matni, serif) .law-quote .plain-mark (oddiy til markeri) .source

export { Button, Spinner } from "./Button.jsx";
export { Card, CardHeader } from "./Card.jsx";
export { Badge, VerifiedBadge, SourceCheckedBadge, UnverifiedBadge, TrustBadge } from "./Badge.jsx";
export { Alert } from "./Alert.jsx";
export { Tabs, TabPanel } from "./Tabs.jsx";
export { Sheet, Modal } from "./Sheet.jsx";
export { Skeleton, SkeletonCard, SkeletonList, EmptyState, Toaster, toast } from "./Feedback.jsx";
export { Reveal, RevealGroup, RevealItem, CountUp, PageTransition, useRevealFallback } from "./Reveal.jsx";
export { Logo } from "./Logo.jsx";
export { Ico, iconFor } from "./icons.jsx";
export { spring, springSnappy, springSheet, fadeUp, stagger, useMediaQuery, useScrolled } from "./motion.js";
export {
  haptic, getWebApp, inTelegram, applyTelegramTheme, installTapHaptics,
  useTelegramBackButton, useTelegramMainButton,
} from "./telegram.js";
