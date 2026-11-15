import React from "react";
import { Composition, staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";
import { Main, PreviewAudio } from "./Main";
import { timeline, totalDurationInFrames } from "./data/timeline";

// Bengali display font — SELF-HOSTED build for this demo project.
// The starter loads Hind Siliguri from Google Fonts; this demo copy loads
// the same font (OFL, Indian Type Foundry) from public/fonts/ instead, so
// rendering works on machines where Google Fonts is unreachable.
// loadFont() holds the render (delayRender) until each face is ready,
// so no frame is ever drawn in a fallback font.
loadFont({
  family: "Hind Siliguri",
  url: staticFile("fonts/HindSiliguri-Regular.ttf"),
  weight: "400",
  style: "normal",
});
loadFont({
  family: "Hind Siliguri",
  url: staticFile("fonts/HindSiliguri-SemiBold.ttf"),
  weight: "600",
  style: "normal",
});
loadFont({
  family: "Hind Siliguri",
  url: staticFile("fonts/HindSiliguri-Bold.ttf"),
  weight: "700",
  style: "normal",
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
