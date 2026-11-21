// Emoji o'rniga lucide ikonkalari. Backend'dan keladigan id'lar (maqom, holat, imtiyoz) → ikonka.
import {
  Baby, BadgeCheck, Bell, BookOpen, Briefcase, Building2, CalendarClock, Car, CircleHelp, FileText, Gift, Globe,
  GraduationCap, HeartHandshake, IdCard, Landmark, MessageCircleQuestion, Receipt, Scale, SearchCheck, Settings,
  ShieldCheck, UserRound, Users,
} from "lucide-react";

const BY_ID = {
  // maqomlar
  uz_citizen: IdCard, foreign: Globe, stateless: UserRound, unknown: CircleHelp,
  // holatlar / toifalar
  student: GraduationCap, parent: Baby, mother: Baby, entrepreneur: Briefcase, legal_entity: Building2,
  pensioner: HeartHandshake, driver: Car, worker: Briefcase, civil_servant: Landmark,
  // bo'limlar
  benefits: Gift, rights: Scale, obligations: CalendarClock, laws: BookOpen, changes: Bell, ask: MessageCircleQuestion,
  account: Settings, edu: GraduationCap, gov: Landmark, mine: Users,
  question: MessageCircleQuestion, sms: Receipt, factcheck: SearchCheck,
};

/** id bo'yicha ikonka komponenti (topilmasa — so'z bo'lagi bo'yicha, keyin FileText) */
export function iconFor(id = "") {
  if (BY_ID[id]) return BY_ID[id];
  const k = Object.keys(BY_ID).find((key) => String(id).includes(key));
  if (k) return BY_ID[k];
  if (/child|bola|alimony|aliment/.test(id)) return Baby;
  if (/pension|elderly/.test(id)) return HeartHandshake;
  if (/fine|jarima/.test(id)) return Car;
  if (/stip|study|talaba/.test(id)) return GraduationCap;
  if (/tax|soliq|business/.test(id)) return Briefcase;
  return FileText;
}

/** Ikonka chipi (.ico): 44×44, radius 14, to'q sariq fon. */
export function Ico({ id, icon: I, size = "md", tone, className = "" }) {
  const C = I || iconFor(id);
  return <span className={`ico ${size === "sm" ? "ico-sm" : ""} ${tone === "ok" ? "ico-ok" : ""} ${className}`} aria-hidden><C strokeWidth={2} /></span>;
}

export { BadgeCheck, ShieldCheck };
