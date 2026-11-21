# Kalao Extension Store

A signed extension repository for [Kalao](https://github.com/kalaoapp/Kalao). Kalao ships no content
sources of its own; every lyrics, metadata or audio source is an extension the user installs.

## Add this repository in Kalao

**Extensions → Repositories → Add repository**, then enter:

```
https://raw.githubusercontent.com/kalaoapp/Kalao-Extensions/main/index.json
```

Kalao shows the repository key's fingerprint before you trust it. It must be:

```
20fa:51ac:baec:e050:ed5c:c58f:9df4:a2b8
```

Every package's SHA-256 and ed25519 signature are checked against this key before it is installed.

## Layout

| Path | Contents |
| --- | --- |
| `index.json` | The signed repository index Kalao reads (generated, do not edit by hand) |
| `extensions/` | `.kalaoext` packages listed in `index.json` |
| `sources/<name>/` | Reviewable source for source-backed packages, with offline fixtures |
| `scripts/build_packages.py` | Packs `sources/` reproducibly and rebuilds the signed index |
| `tests/` | Checks that the index, packages, checksums and signatures agree |

## Submit your extension

1. Fork this repository.
2. Add your extension's source folder to `sources/<name>/` (`manifest.json`, `index.js`, optional
   `icon.png` and `lib/`), with offline fixtures in `fixtures/tests.json`. See the
   [extension guide](https://github.com/kalaoapp/Kalao/blob/main/android/docs/EXTENSIONS.md) for the
   manifest, the `kalao` API and `kalao-ext`.
3. Check it locally:
   ```sh
   kalao-ext validate sources/<name>
   kalao-ext test sources/<name>
   ```
4. Open a pull request. Do not add a package or edit `index.json`; the maintainer builds and signs
   them after review.

## Requirements

- Source is readable JavaScript: no minified or obfuscated code, no bundled binaries.
- Network access is limited to the hosts the extension needs, declared in `network.hosts`.
- No API keys, tokens or credentials in the source. Settings may ask the user for their own.
- A clear `description` of what the extension does and which service it uses.
- The extension respects the terms of the sites it accesses. Extensions are their author's
  responsibility.
- Offline fixtures cover each exported capability.

## Building packages (maintainer)

`kalao-ext` comes from the Kalao repository:

```sh
git clone https://github.com/kalaoapp/Kalao && cd Kalao/rust_backend
cargo build --locked --release -p kalao-ext      # target/release/kalao-ext
```

Edit a source, bump its manifest `version`, then:

```sh
python3 scripts/build_packages.py --kalao-ext path/to/kalao-ext --key path/to/kalao-extensions.key
python3 scripts/build_packages.py --kalao-ext path/to/kalao-ext --check
python3 -m unittest discover -s tests -p 'test_*.py'
```

The build validates each source, runs its offline fixtures, packs it into
`extensions/<name>.kalaoext` and re-signs `index.json` from every package in `extensions/`. Pass
source directory names to rebuild a subset, for example `python3 scripts/build_packages.py lrclib`.
`--check` needs no key; CI uses it to confirm that committed packages match their sources.

Commit source, packages and `index.json` together. The secret key never enters this repository.
Changing it blocks updates until every user removes and re-adds the repository, so the build refuses
a different key unless `--rotate-key` is passed.

## Extensions

| Extension | ID | Capabilities |
| --- | --- | --- |
| [LRCLIB](sources/lrclib/) | `app.kalao.lrclib` | Synced and plain lyrics from [lrclib.net](https://lrclib.net) |

## Review process

All submissions are reviewed before they are added to the store.

## License

This repository is licensed under the [GNU General Public License v3.0 only](LICENSE). The repository
layout and build scripts are adapted from
[Mornye-Extension](https://github.com/mornyeapp/Mornye-Extension) (Copyright 2026 zarzet,
LGPL-3.0-only); see [NOTICE](NOTICE). Third-party extensions retain their own license notices.
