import React from "react";
import { Composition } from "remotion";
import { loadFont } from "@remotion/google-fonts/HindSiliguri";
import { Main, PreviewAudio } from "./Main";
import { FPS, totalDurationInFrames } from "./timing";

// Bengali display font — weights used across the scenes.
// loadFont() holds the render (delayRender) until the font is ready,
// so no frame is ever drawn in a fallback font.
loadFont("normal", {
  weights: ["400", "600", "700"],
  subsets: ["bengali", "latin"],
});

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Main"
        component={Main}
        durationInFrames={totalDurationInFrames}
        fps={FPS}
        width={1920}
        height={1080}
        calculateMetadata={() => ({
          durationInFrames: totalDurationInFrames,
        })}
      />
      <Composition
        id="PreviewAudio"
        component={PreviewAudio}
        durationInFrames={totalDurationInFrames}
        fps={FPS}
        width={1920}
        height={1080}
        calculateMetadata={() => ({
          durationInFrames: totalDurationInFrames,
        })}
      />
    </>
  );
};
