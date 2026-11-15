import React from "react";
import { useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WordByWord } from "../components/WordByWord";
import { CounterUp, DrawLine } from "../components/anim";
import { extractNumbers, splitChunks } from "../components/chunks";
import type { SceneProps } from "../data/timeline";
import { theme } from "../theme";

const BN_DIGITS = "০১২৩৪৫৬৭৮৯";

const toAsciiDigits = (value: string): string =>
  value.replace(/[০-৯]/g, (d) => String(BN_DIGITS.indexOf(d)));

const toBnDigits = (value: string): string =>
  value.replace(/[0-9]/g, (d) => BN_DIGITS[Number(d)]);

interface ParsedToken {
  raw: string;
  value: number;
  suffix: string;
  decimals: number;
  isBengali: boolean;
}

const parseToken = (raw: string): ParsedToken => {
  const suffix = raw.includes("%") ? "%" : "";
  const numericRaw = toAsciiDigits(
    raw.replace(/[%৳$]/g, "").replace(/,/g, "").trim(),
  );
  const value = parseFloat(numericRaw);
  return {
    raw,
    value: Number.isFinite(value) ? value : 0,
    suffix,
    decimals: numericRaw.includes(".")
      ? numericRaw.split(".")[1].length
      : 0,
    isBengali: /[০-৯]/.test(raw),
  };
};

/**
 * ScoreboardScene — Scoreboard genre scene (scoreboard), data-driven.
 * Numbers come only from the cue (extractNumbers) and count up big;
 * each raw token stays as its label. A cue with no numbers shows
 * its chunks as rows separated by drawn lines instead.
 */
export const ScoreboardScene: React.FC<SceneProps> = ({ scene }) => {
  const { width } = useVideoConfig();
  const s = width / 1920;
  const tokens = extractNumbers(scene.text).slice(0, 4);
  const parsed = tokens.map(parseToken);
  const chunks = splitChunks(scene.text, 4);

  return (
    <SceneShell
      kicker="Scoreboard"
      style={{ backgroundColor: "#0B0F14" }}
    >
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          border: `3px solid ${theme.accent}`,
          borderRadius: theme.radius,
          padding: `${44 * s}px ${52 * s}px`,
          boxSizing: "border-box",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <WordByWord
            text={scene.text}
            style={{ fontSize: 40 * s, fontWeight: 600, lineHeight: 1.35 }}
          />
        </div>
        {parsed.length > 0 ? (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexWrap: "wrap",
              alignItems: "center",
              justifyContent: "center",
              gap: 56 * s,
              marginTop: 32 * s,
            }}
          >
            {parsed.map((token, i) => (
              <div
                key={`${token.raw}-${i}`}
                style={{ textAlign: "center", minWidth: 260 * s }}
              >
                <CounterUp
                  value={token.value}
                  suffix={token.suffix}
                  decimals={token.decimals}
                  durationInFrames={50}
                  delay={10 + i * 8}
                  format={
                    token.isBengali
                      ? (current) =>
                          toBnDigits(current.toFixed(token.decimals))
                      : undefined
                  }
                  style={{
                    fontSize: 110 * s,
                    fontWeight: 700,
                    color: theme.fg,
                    fontVariantNumeric: "tabular-nums",
                  }}
                />
                <div
                  style={{
                    marginTop: 10 * s,
                    fontSize: 30 * s,
                    color: theme.muted,
                    letterSpacing: 0,
                  }}
                >
                  {token.raw}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              marginTop: 24 * s,
            }}
          >
            {chunks.map((chunk, i) => (
              <React.Fragment key={`${chunk}-${i}`}>
                {i > 0 ? (
                  <div
                    style={{
                      position: "relative",
                      height: 28 * s,
                    }}
                  >
                    <DrawLine
                      x1={60}
                      y1={540}
                      x2={1860}
                      y2={540}
                      delay={8 + i * 6}
                      durationInFrames={16}
                      color={theme.accent}
                      strokeWidth={3}
                    />
                  </div>
                ) : null}
                <div
                  style={{
                    fontSize: 44 * s,
                    fontWeight: 600,
                    lineHeight: 1.4,
                    textAlign: "center",
                    padding: `${14 * s}px 0`,
                    letterSpacing: 0,
                  }}
                >
                  {chunk}
                </div>
              </React.Fragment>
            ))}
          </div>
        )}
      </div>
    </SceneShell>
  );
};
