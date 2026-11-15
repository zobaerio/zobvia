export interface Theme {
  /** Page / scene background. */
  bg: string;
  /** Primary text colour. */
  fg: string;
  /** The ONE accent colour for this video (CREATE mode asks only this). */
  accent: string;
  /** Companion accent 2 (v1.4 multi-colour system, WCAG AA on bg). */
  accent2: string;
  /** Companion accent 3 (v1.4 multi-colour system, WCAG AA on bg). */
  accent3: string;
  /** Low-opacity tint of the accent, for tiles / chips / bar fills. */
  accentSoft: string;
  /** Secondary / de-emphasised text. */
  muted: string;
  /** Bengali-safe display font. Never set letterSpacing with it. */
  font: string;
  radius: number;
  gap: number;
}

export const theme: Theme = {
  bg: "#0B0F14",
  fg: "#F5F7FA",
  accent: "#FFB020",
  accent2: "#22D3EE",
  accent3: "#FB7185",
  accentSoft: "rgba(255, 176, 32, 0.14)",
  muted: "#9AA7B4",
  font: "Hind Siliguri",
  radius: 24,
  gap: 28,
};

/**
 * v1.4 multi-colour system: the headline colour rotates through the
 * three accents by scene position (0-based), so consecutive scenes do
 * not all wear the same colour. Body text always stays theme.fg.
 * Consumed by SceneShell (kicker + counter chip) and WordByWord
 * (headline base colour, via SceneMetaContext).
 */
export const SCENE_ACCENTS: string[] = [
  theme.accent,
  theme.accent2,
  theme.accent3,
];

export const sceneAccent = (index: number): string =>
  SCENE_ACCENTS[((index % SCENE_ACCENTS.length) + SCENE_ACCENTS.length) %
    SCENE_ACCENTS.length];
