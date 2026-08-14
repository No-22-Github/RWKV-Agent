import {
  sourceColorFromImageBytes,
  SchemeTonalSpot,
  MaterialDynamicColors,
  Hct,
  hexFromArgb,
  Blend,
} from "@material/material-color-utilities";

const STORAGE_KEY = "rwkv-theme-argb";
const DARK_KEY = "rwkv-theme-dark";
const mdc = new MaterialDynamicColors();

// RWKV 品牌蓝作为默认 Monet 种子色
const DEFAULT_SEED = 0xff5f8df7;

let currentArgb = DEFAULT_SEED;
let currentDark = false;

function applyScheme(scheme: SchemeTonalSpot, isDark: boolean): void {
  const root = document.documentElement;
  const set = (token: string, argb: number) => root.style.setProperty(token, hexFromArgb(argb));

  root.setAttribute("data-theme", isDark ? "dark" : "light");
  root.style.colorScheme = isDark ? "dark" : "light";

  // Primary
  set("--md-sys-color-primary",                mdc.primary().getArgb(scheme));
  set("--md-sys-color-on-primary",             mdc.onPrimary().getArgb(scheme));
  set("--md-sys-color-primary-container",      mdc.primaryContainer().getArgb(scheme));
  set("--md-sys-color-on-primary-container",   mdc.onPrimaryContainer().getArgb(scheme));

  // Secondary
  set("--md-sys-color-secondary",              mdc.secondary().getArgb(scheme));
  set("--md-sys-color-on-secondary",           mdc.onSecondary().getArgb(scheme));
  set("--md-sys-color-secondary-container",    mdc.secondaryContainer().getArgb(scheme));
  set("--md-sys-color-on-secondary-container", mdc.onSecondaryContainer().getArgb(scheme));

  // Tertiary
  set("--md-sys-color-tertiary",               mdc.tertiary().getArgb(scheme));
  set("--md-sys-color-on-tertiary",            mdc.onTertiary().getArgb(scheme));
  set("--md-sys-color-tertiary-container",     mdc.tertiaryContainer().getArgb(scheme));
  set("--md-sys-color-on-tertiary-container",  mdc.onTertiaryContainer().getArgb(scheme));

  // Error
  set("--md-sys-color-error",                  mdc.error().getArgb(scheme));
  set("--md-sys-color-on-error",               mdc.onError().getArgb(scheme));
  set("--md-sys-color-error-container",        mdc.errorContainer().getArgb(scheme));
  set("--md-sys-color-on-error-container",     mdc.onErrorContainer().getArgb(scheme));

  // Background
  set("--md-sys-color-background",             mdc.background().getArgb(scheme));
  set("--md-sys-color-on-background",          mdc.onBackground().getArgb(scheme));

  // Surface — full MD3 surface system
  set("--md-sys-color-surface",                mdc.surface().getArgb(scheme));
  set("--md-sys-color-on-surface",             mdc.onSurface().getArgb(scheme));
  set("--md-sys-color-surface-dim",            mdc.surfaceDim().getArgb(scheme));
  set("--md-sys-color-surface-bright",         mdc.surfaceBright().getArgb(scheme));
  set("--md-sys-color-surface-variant",        mdc.surfaceVariant().getArgb(scheme));
  set("--md-sys-color-on-surface-variant",     mdc.onSurfaceVariant().getArgb(scheme));
  set("--md-sys-color-surface-container-lowest",  mdc.surfaceContainerLowest().getArgb(scheme));
  set("--md-sys-color-surface-container-low",     mdc.surfaceContainerLow().getArgb(scheme));
  set("--md-sys-color-surface-container",         mdc.surfaceContainer().getArgb(scheme));
  set("--md-sys-color-surface-container-high",    mdc.surfaceContainerHigh().getArgb(scheme));
  set("--md-sys-color-surface-container-highest",  mdc.surfaceContainerHighest().getArgb(scheme));
  set("--md-sys-color-surface-tint",           mdc.primary().getArgb(scheme));

  // Outline
  set("--md-sys-color-outline",                mdc.outline().getArgb(scheme));
  set("--md-sys-color-outline-variant",        mdc.outlineVariant().getArgb(scheme));

  // Inverse
  set("--md-sys-color-inverse-surface",        mdc.inverseSurface().getArgb(scheme));
  set("--md-sys-color-inverse-on-surface",     mdc.inverseOnSurface().getArgb(scheme));
  set("--md-sys-color-inverse-primary",        mdc.inversePrimary().getArgb(scheme));

  // Shadow & scrim
  set("--md-sys-color-shadow",                 mdc.shadow().getArgb(scheme));
  set("--md-sys-color-scrim",                  mdc.scrim().getArgb(scheme));

  // Custom harmonized colors — success & warning
  const sourceArgb = mdc.primary().getArgb(scheme);
  const successBase = 0xff4caf50; // green 500
  const warningBase = 0xffffc107; // amber 500

  const successHarmonized = Blend.harmonize(successBase, sourceArgb);
  const warningHarmonized = Blend.harmonize(warningBase, sourceArgb);

  const successHct = Hct.fromInt(successHarmonized);
  const warningHct = Hct.fromInt(warningHarmonized);

  // Light: color=40, onColor=100, container=90, onContainer=10
  // Dark:  color=80, onColor=20,  container=30, onContainer=90
  const ct = isDark ? [80, 20, 30, 90] : [40, 100, 90, 10];

  root.style.setProperty("--md-custom-color-success",              hexFromArgb(Hct.from(successHct.hue, successHct.chroma, ct[0]).toInt()));
  root.style.setProperty("--md-custom-color-on-success",           hexFromArgb(Hct.from(successHct.hue, successHct.chroma, ct[1]).toInt()));
  root.style.setProperty("--md-custom-color-success-container",    hexFromArgb(Hct.from(successHct.hue, successHct.chroma, ct[2]).toInt()));
  root.style.setProperty("--md-custom-color-on-success-container", hexFromArgb(Hct.from(successHct.hue, successHct.chroma, ct[3]).toInt()));

  root.style.setProperty("--md-custom-color-warning",              hexFromArgb(Hct.from(warningHct.hue, warningHct.chroma, ct[0]).toInt()));
  root.style.setProperty("--md-custom-color-on-warning",           hexFromArgb(Hct.from(warningHct.hue, warningHct.chroma, ct[1]).toInt()));
  root.style.setProperty("--md-custom-color-warning-container",    hexFromArgb(Hct.from(warningHct.hue, warningHct.chroma, ct[2]).toInt()));
  root.style.setProperty("--md-custom-color-on-warning-container", hexFromArgb(Hct.from(warningHct.hue, warningHct.chroma, ct[3]).toInt()));
}

function applyArgb(argb: number, isDark: boolean): void {
  currentArgb = argb;
  currentDark = isDark;
  applyScheme(new SchemeTonalSpot(Hct.fromInt(argb), isDark, 0), isDark);
}

/** 将图片缩小到 maxSize 后提取像素，避免大图阻塞主线程 */
function downsampleImageBytes(img: HTMLImageElement, maxSize = 128): Uint8ClampedArray {
  const scale = Math.min(1, maxSize / Math.max(img.naturalWidth, img.naturalHeight));
  const w = Math.max(1, Math.round(img.naturalWidth * scale));
  const h = Math.max(1, Math.round(img.naturalHeight * scale));
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  canvas.getContext("2d")!.drawImage(img, 0, 0, w, h);
  return canvas.getContext("2d")!.getImageData(0, 0, w, h).data;
}

export async function applyThemeFromImage(img: HTMLImageElement): Promise<number> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const bytes = downsampleImageBytes(img);
      const argb = sourceColorFromImageBytes(bytes);
      applyArgb(argb, currentDark);
      localStorage.setItem(STORAGE_KEY, String(argb));
      resolve(argb);
    }, 0);
  });
}

export function applyDefaultTheme(): void {
  const savedDark = localStorage.getItem(DARK_KEY);
  currentDark = savedDark !== null
    ? savedDark === "true"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;

  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    applyArgb(Number(saved), currentDark);
  } else {
    applyArgb(DEFAULT_SEED, currentDark);
  }
}

/** 手动设置强调色种子（供设置里的取色器使用） */
export function applySeedColor(argb: number): void {
  applyArgb(argb, currentDark);
  localStorage.setItem(STORAGE_KEY, String(argb));
}

export function toggleDarkMode(): boolean {
  currentDark = !currentDark;
  localStorage.setItem(DARK_KEY, String(currentDark));
  applyArgb(currentArgb, currentDark);
  return currentDark;
}

export function isDark(): boolean {
  return currentDark;
}