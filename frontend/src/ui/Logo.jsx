import { APP_NAME } from "../config.js";

/**
 * Logo — yagona joy. Belgini almashtirish uchun faqat frontend/public/logo.svg ni yangilang.
 * withText=false — faqat belgi.
 */
export function Logo({ size = 32, withText = true, href, onClick, className = "", textClassName = "" }) {
  const inner = (
    <>
      <img src="/logo.svg" width={size} height={size} alt={withText ? "" : APP_NAME} />
      {withText && <span className={`logo-text ${textClassName}`}>{APP_NAME}</span>}
    </>
  );
  if (href) {
    return <a href={href} onClick={onClick} className={`logo ${className}`} aria-label={`${APP_NAME} — bosh sahifa`}>{inner}</a>;
  }
  return <span className={`logo ${className}`}>{inner}</span>;
}
