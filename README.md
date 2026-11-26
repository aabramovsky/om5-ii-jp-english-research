# English menus in the Japanese slot of the OM-5 Mark II

Research for the **native OM SYSTEM OM-5 Mark II (E148), official firmware 1.1**.
An owner of one Japanese-market body reports a normal boot and English stock
menus after installing the resource-only r01 output. Post-install functional
testing is **partial**: the owner reported no problems in the subset tried, but
did not specify every completed item. Complete UI coverage, reliability and
recovery have not been established.

This is an experimental research result, not a generally validated release.
It is not for the original OM-5/E144, or an OM-5-to-Mark-II firmware port.

## What changes

Only resource component **0101** is included in the 12 MiB experimental package.
The Japanese string descriptor points to an appended table assembled from the
firmware's existing English strings plus **39 explicitly identified research
translations** for entries empty in English but populated in Japanese. The
original Japanese font and all other resource records are preserved.

The method does not rewrite the region configuration or add an OMKit loader.
Executable components are absent from the resource-only package. This is English
text in the Japanese slot, not proof that the language selector was unlocked.

## Read first

- [Illustrated human guide](START_HERE.html) — download/open locally in a browser.
- [Detailed context for AI agents and technical reviewers](AGENT_CONTEXT.md)
- [Design and exact ranges](docs/design.md)
- [One-camera report and evidence boundaries](docs/hardware-result.md)
- [Validation and unresolved risks](docs/validation.md)
- [Sources and credits](docs/credits.md)

Updating even this resource-only package erases the entire selected 12 MiB
resource range before writing. The device can become unbootable; independent
recovery after a damaged resource component is unknown. A successful build,
checksum, emulator run or previous boot does not establish safety for another body.

## Offline reproduction

Python 3.9+ and the standard library are sufficient. Supply your own exact
official E148/1.1 input. No firmware is downloaded or included in this repository.

```sh
python -B -m unittest discover -s tests -v
python -B tools/reproduce.py --stock /path/to/OLY_E_148_1100_0000_0000.BIN
```

The second command builds in memory, validates the pinned output hashes and prints
a compact result. It writes no firmware unless an output directory is explicitly
provided:

```sh
python -B tools/reproduce.py --stock /path/to/stock.BIN --output-dir /path/to/new-research-output
```

The output directory must not already exist. After staged writes and disk
size/hash readback, it receives two `.research-bin` files and a small manifest.
If `.INCOMPLETE` remains after an error, the output set is unfinished and must
not be treated as a successful build. The tool has no device transport, camera commands,
SD discovery, automatic installation or updater filenames. Keep outputs outside
the source checkout and out of published archives.

Optional integration tests use a separately supplied input:

```sh
# POSIX shell
OM5_TEST_STOCK=/path/to/stock.BIN python -B -m unittest discover -s tests -v
```

```powershell
# PowerShell
$env:OM5_TEST_STOCK='D:\firmware\stock.BIN'
python -B -m unittest discover -s tests -v
```

## Exact artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official full E148/1.1 input | 90,832,896 | `9de5d77e1d290fa2ed4ebc7d75cee0ed490befbc89566722467d1d421d66d637` |
| Intermediate full r01, in memory only | 90,832,896 | `68f5d1e8f7c2ed7c64a238b0f9ccfb8446ae9c78117ed632df930c7f44e16ad5` |
| r01 resource-only output | 12,582,912 | `82aebb31264c29ce64921f8cecdc8a431a780df6d281d14b5706a2f85dc602fc` |
| Stock resource-only reference | 12,582,912 | `ff68b7bf98b1f7ff90a69b0d46c1c3e2c68673021bbc94f93c7b39b196fdd2cf` |

The full r01 was not the installed image. The stock reference is not an
independent rescue loader. Exact model/build/hash mismatches are rejected.

## Contributions

Useful contributions include independent reproduction, translation/layout
corrections, additional non-destructive UI observations and better evidence about
startup/recovery dependencies. State the exact camera, base version, artifact hash,
test environment and limitations. Never include serial numbers, credentials,
network identifiers, personal metadata or proprietary firmware in an issue/PR.

Research and packaging were assisted by AI coding/review agents. The physical
camera was operated by its owner; software checks and owner reports are
distinguished throughout. AI review is not a hardware-safety certification.
