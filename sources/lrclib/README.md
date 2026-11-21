# LRCLIB

Synced and plain lyrics from [LRCLIB](https://lrclib.net), an open lyrics database with no API key.
This is Kalao's public sample extension (`examples/extensions/lrclib` in
[kalaoapp/Kalao](https://github.com/kalaoapp/Kalao)); copy this folder to start your own.

- Capability: `lyrics` (`searchLyrics`, `getLyrics`)
- Network: `lrclib.net`
- Setting: **Only synced lyrics**

```sh
kalao-ext validate sources/lrclib
kalao-ext test sources/lrclib      # offline, against fixtures/tests.json
```
