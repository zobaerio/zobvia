import React from "react";
import {
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";

/**
 * anim.tsx — reusable frame-driven animation helpers.
 *
 * Every helper is driven only by useCurrentFrame() / spring() /
 * interpolate() from Remotion, so renders stay deterministic.
 * Text-bearing helpers keep letterSpacing: 0 and never split
 * grapheme clusters (Bengali conjuncts stay whole).
 */

const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

// ---------------------------------------------------------------- FadeUp

export interface FadeUpProps {
  children: React.ReactNode;
  delay?: number;
  distance?: number;
  style?: React.CSSProperties;
}

export const FadeUp: React.FC<FadeUpProps> = ({
  children,
  delay = 0,
  distance = 28,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, 12], [0, 1], CLAMP);
  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${(1 - progress) * distance}px)`,
        letterSpacing: 0,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// -------------------------------------------------------------- SpringPop

export interface SpringPopProps {
  children: React.ReactNode;
  delay?: number;
  from?: number;
  style?: React.CSSProperties;
}

export const SpringPop: React.FC<SpringPopProps> = ({
  children,
  delay = 0,
  from = 0.6,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, stiffness: 180, mass: 0.6 },
  });
  const scale = from + (1 - from) * pop;
  return (
    <div
      style={{
        opacity: pop,
        transform: `scale(${scale})`,
        letterSpacing: 0,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// ---------------------------------------------------------------- BlurIn

export interface BlurInProps {
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
}

export const BlurIn: React.FC<BlurInProps> = ({
  children,
  delay = 0,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, 12], [0, 1], CLAMP);
  const blur = interpolate(progress, [0, 1], [12, 0]);
  return (
    <div
      style={{
        opacity: progress,
        filter: blur > 0.01 ? `blur(${blur}px)` : undefined,
        letterSpacing: 0,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// ------------------------------------------------------------- CounterUp

export interface CounterUpProps {
  value: number;
  suffix?: string;
  decimals?: number;
  durationInFrames?: number;
  delay?: number;
  format?: (current: number) => string;
  style?: React.CSSProperties;
}

export const CounterUp: React.FC<CounterUpProps> = ({
  value,
  suffix = "",
  decimals = 0,
  durationInFrames = 50,
  delay = 0,
  format,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, durationInFrames], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.cubic),
  });
  const current = value * progress;
  const rendered = format ? format(current) : current.toFixed(decimals);
  return (
    <span style={{ letterSpacing: 0, ...style }}>
      {rendered}
      {suffix}
    </span>
  );
};

// -------------------------------------------------------------- DrawLine

export interface DrawLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  delay?: number;
  durationInFrames?: number;
  color: string;
  strokeWidth?: number;
}

export const DrawLine: React.FC<DrawLineProps> = ({
  x1,
  y1,
  x2,
  y2,
  delay = 0,
  durationInFrames = 16,
  color,
  strokeWidth = 3,
}) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame - delay, [0, durationInFrames], [0, 1], CLAMP);
  return (
    <svg
      viewBox="0 0 1920 1080"
      preserveAspectRatio="none"
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    >
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth={strokeWidth}
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - draw}
      />
    </svg>
  );
};

// ------------------------------------------------------------- ShineText

export interface ShineTextProps {
  text: string;
  style?: React.CSSProperties;
}

export const ShineText: React.FC<ShineTextProps> = ({ text, style }) => {
  const frame = useCurrentFrame();
  const cycle = frame % 90;
  const position = interpolate(cycle, [0, 90], [120, -20], CLAMP);
  return (
    <span
      style={{
        background: `linear-gradient(100deg, ${theme.fg} 40%, ${theme.accent} 50%, ${theme.fg} 60%)`,
        backgroundSize: "220% 100%",
        backgroundPosition: `${position}% 0%`,
        WebkitBackgroundClip: "text",
        backgroundClip: "text",
        color: "transparent",
        letterSpacing: 0,
        ...style,
      }}
    >
      {text}
    </span>
  );
};

// ---------------------------------------------------------------- FloatY

export interface FloatYProps {
  children: React.ReactNode;
  amplitude?: number;
  period?: number;
  style?: React.CSSProperties;
}

export const FloatY: React.FC<FloatYProps> = ({
  children,
  amplitude = 10,
  period = 90,
  style,
}) => {
  const frame = useCurrentFrame();
  const translateY = Math.sin((frame / period) * Math.PI * 2) * amplitude;
  return (
    <div
      style={{
        transform: `translateY(${translateY}px)`,
        letterSpacing: 0,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// ------------------------------------------------------------ GlitchSlice

export interface GlitchSliceProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export const GlitchSlice: React.FC<GlitchSliceProps> = ({
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const cycle = frame % 75;
  const glitching = cycle < 4;
  return (
    <div style={{ position: "relative", letterSpacing: 0, ...style }}>
      <div>{children}</div>
      {glitching ? (
        <>
          <div
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              clipPath: "inset(0 0 66% 0)",
              transform: "translateX(-7px)",
              opacity: 0.55,
              filter: "hue-rotate(60deg) saturate(2)",
              pointerEvents: "none",
              letterSpacing: 0,
            }}
          >
            {children}
          </div>
          <div
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              clipPath: "inset(66% 0 0 0)",
              transform: "translateX(7px)",
              opacity: 0.55,
              filter: "hue-rotate(-60deg) saturate(2)",
              pointerEvents: "none",
              letterSpacing: 0,
            }}
          >
            {children}
          </div>
        </>
      ) : null}
    </div>
  );
};
