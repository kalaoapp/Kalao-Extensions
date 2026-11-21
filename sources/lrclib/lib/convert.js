// One LRCLIB record → a Kalao lyrics candidate (EXTENSIONS.md §4).
export function toCandidate(item) {
  if (!item || item.instrumental) return null;
  const synced = typeof item.syncedLyrics === "string" && item.syncedLyrics.trim() !== "";
  const plain = typeof item.plainLyrics === "string" && item.plainLyrics.trim() !== "";
  if (!synced && !plain) return null;
  return {
    id: String(item.id),
    title: item.trackName || item.name || "",
    artist: item.artistName || "",
    album: item.albumName || undefined,
    durationMs: typeof item.duration === "number" ? Math.round(item.duration * 1000) : undefined,
    format: synced ? "lrc" : "plain",
    body: synced ? item.syncedLyrics : item.plainLyrics,
  };
}
