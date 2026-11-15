import React from "react";
import { Composition } from "remotion";
import { loadFont } from "@remotion/google-fonts/HindSiliguri";
import { Main, PreviewAudio } from "./Main";
import { timeline, totalDurationInFrames } from "./data/timeline";

// Bengali display font — weights used across the scenes.
// loadFont() holds the render (delayRender) until the font is ready,
// so no frame is ever drawn in a fallback font.
loadFont("normal", {
  weights: ["400", "600", "700"],
  subsets: ["bengali", "latin"],
});

/**
 * Composition geometry comes from src/data/timeline.json — fps, width,
 * height and duration all follow the generated timeline, so a 9:16 or
 * 1:1 project needs no code changes here.
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Main"
        component={Main}
        durationInFrames={totalDurationInFrames}
        fps={timeline.fps}
        width={timeline.width}
        height={timeline.height}
        calculateMetadata={() => ({
          durationInFrames: totalDurationInFrames,
        })}
      />
      <Composition
        id="PreviewAudio"
        component={PreviewAudio}
        durationInFrames={totalDurationInFrames}
        fps={timeline.fps}
        width={timeline.width}
        height={timeline.height}
        calculateMetadata={() => ({
          durationInFrames: totalDurationInFrames,
        })}
      />
    </>
  );
};
