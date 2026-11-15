export interface Theme {
  /** Page / scene background. */
  bg: string;
  /** Primary text colour. */
  fg: string;
  /** The ONE accent colour for this video (CREATE mode asks only this). */
  accent: string;
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
  accentSoft: "rgba(255, 176, 32, 0.14)",
  muted: "#9AA7B4",
  font: "Hind Siliguri",
  radius: 24,
  gap: 28,
};
