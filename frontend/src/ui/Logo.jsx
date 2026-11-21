import { APP_NAME } from "../config.js";

/**
 * Logo — yagona joy. Fayllar: frontend/public/huquqim_horizontal_{dark,light}.png (brand/ dan).
 * Qorong'i rejimda _dark, yorug'da _light ko'rinadi (CSS: --logo-dark / --logo-light).
 */
export function Logo({ height = 36, href, onClick, className = "" }) {
  const w = Math.round(height * 4);
  const inner = (
    <>
      <img className="logo-img dark" src="/huquqim_horizontal_dark.png" width={w} height={height} style={{ height }} alt={APP_NAME} />
      <img className="logo-img light" src="/huquqim_horizontal_light.png" width={w} height={height} style={{ height }} alt={APP_NAME} />
    </>
  );
  if (href) return <a href={href} onClick={onClick} className={`logo ${className}`} aria-label={`${APP_NAME} — bosh sahifa`}>{inner}</a>;
  return <span className={`logo ${className}`}>{inner}</span>;
}
