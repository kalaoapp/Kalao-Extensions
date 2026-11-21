# Extension Submission

**Extension Name:**
`[e.g. LRCLIB]`

**Extension ID:**
`[e.g. dev.example.lrcfinder]`

**Version:**
`[e.g. 1.0.0]`

**Capabilities:**
`[e.g. lyrics, metadata]`

**Network hosts:**
`[e.g. lrclib.net]`

**Description:**
[Brief description of what the extension does and which service it uses]

**Checklist:**

- [ ] I have added the source folder to `sources/<name>/` (`manifest.json`, `index.js`, optional `icon.png` and `lib/`).
- [ ] `kalao-ext validate sources/<name>` passes.
- [ ] `fixtures/tests.json` covers each capability and `kalao-ext test sources/<name>` passes offline.
- [ ] I have not added a `.kalaoext` package or edited `index.json` (the maintainer builds and signs them).
- [ ] The source is readable, contains no API keys or credentials, and only contacts the hosts it declares.
- [ ] This extension contains no malicious code and respects the terms of the sites it accesses.

**Notes:**
[Any additional information for the reviewers]
