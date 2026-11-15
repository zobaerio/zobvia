import { splitGraphemes } from "./WordByWord";

/**
 * Split scene text into up to `max` display chunks, for tile/node
 * layouts (Bento, Timeline). Splits on sentence ends (। . ! ?), commas
 * and dashes first; if that yields fewer than 2 chunks, falls back to
 * balanced word groups. Text itself is never altered — chunks are
 * exact substrings (trimmed) of the scene text.
 */
export const splitChunks = (text: string, max = 4): string[] => {
  const byPunctuation = text
    .split(/(?<=[।.!?])\s+|,\s+|—\s+|–\s+/)
    .map((part) => part.trim())
    .filter(Boolean);
  if (byPunctuation.length >= 2) {
    return byPunctuation.slice(0, max);
  }
  const words = text.split(/\s+/).filter(Boolean);
  if (words.length < 2) {
    return [text];
  }
  const groups = Math.min(max, Math.ceil(words.length / 3));
  const perGroup = Math.ceil(words.length / groups);
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += perGroup) {
    chunks.push(words.slice(i, i + perGroup).join(" "));
  }
  return chunks.slice(0, max);
};

/**
 * Truncate to at most `maxWords` words, cutting on a word boundary and
 * marking the cut with an ellipsis. Grapheme-safe: words are kept whole,
 * so Bengali conjuncts are never split.
 */
export const truncateWords = (text: string, maxWords: number): string => {
  const words = text.split(/\s+/).filter(Boolean);
  if (words.length <= maxWords) {
    return text;
  }
  return `${words.slice(0, maxWords).join(" ")}…`;
};

/** Grapheme count of a string (Bengali-safe length measure). */
export const graphemeLength = (text: string): number =>
  splitGraphemes(text).length;
