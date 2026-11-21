// LRCLIB lyrics for Kalao: the public sample extension (EXTENSIONS.md §8).
// API: https://lrclib.net/docs. No key; please identify the client.
import { toCandidate } from "./lib/convert.js";

const API = "https://lrclib.net/api";
const HEADERS = { "Lrclib-Client": "Kalao LRCLIB extension 1.0.0 (https://github.com/kalaoapp/Kalao)" };

async function getJson(url) {
  const res = await kalao.fetch(url, { headers: HEADERS, timeoutMs: 6000 });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("LRCLIB answered HTTP " + res.status);
  return res.json();
}

export async function searchLyrics(query) {
  const syncedOnly = kalao.settings.get("syncedOnly") === true;
  const params = query.artist
    ? { track_name: query.title, artist_name: query.artist, album_name: query.album }
    : { q: query.title };
  const items = (await getJson(API + "/search?" + kalao.url.params(params))) || [];
  return items
    .map(toCandidate)
    .filter((candidate) => candidate && (!syncedOnly || candidate.format === "lrc"))
    .slice(0, 20);
}

export async function getLyrics(id) {
  const item = await getJson(API + "/get/" + encodeURIComponent(id));
  const candidate = item && toCandidate(item);
  if (!candidate) throw new Error("LRCLIB has no lyrics for " + id);
  return candidate;
}
