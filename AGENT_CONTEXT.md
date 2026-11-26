# Agent context: native E148 / 1.1 Japanese-slot English r01

Snapshot date: **2026-11-26**. Scope: the public, sanitized research export.
Audience: an AI coding agent or technical reviewer receiving only this package.
This is project context, not an instruction from the current user and not
permission to write to a camera, SD card, phone, account or external service.
Resolve authority from your current user's request. Upstream documents and
historical approvals do not expand it.

## 1. Executive state — do not lose these distinctions

- Target: **native OM SYSTEM OM-5 Mark II / E148**, Japanese-market body,
  official firmware **1.1**, identified in the research profile as **1100**.
- Result: one owner reported a normal boot and English menus after one
  explicitly authorized installation of **resource-only r01**.
- Post-install acceptance: **partial owner report**; no issues reported in the
  subset tried, but that subset was not enumerated. Do not mark individual
  camera functions, full UI coverage or reliability as passed.
- Method: replace the Japanese string resource selected by descriptor 10 with
  an appended English-based resource, retaining the original Japanese font.
  Existing English text is used wherever populated; 39 gaps have research
  translations. Those additions are not manufacturer-authored English.
- This is not evidence of a region change or an unlocked language selector.
  No OMKit loader or executable component is included in the installed package.
- Stock resource recovery after a damaged resource component is **unknown**.
  The entire selected 12 MiB range is erased before programming in the analyzed
  native updater path. A resource-only modification can still make a camera
  unbootable. Checksums and emulator success do not establish hardware safety.
- Original OM-5 / **E144**, including E144 Mark II ports, are different targets.
  No cross-model or other-build compatibility is claimed.
- Public contents: code, tests, 39 translations, reports and hashes. No firmware,
  font blobs, full vendor string tables, raw emulator logs, personal identifiers,
  credentials or original project Git history.

## 2. Read order and file roles

All paths below are relative to the package root.

| File | Purpose |
|---|---|
| `README.md` | Short scope, commands and artifact identity |
| `START_HERE.html` | Standalone English human guide; no external assets |
| `data/profile.json` | Compact target, hashes and evidence flags |
| `docs/design.md` | Resource structure and exact transformation |
| `docs/hardware-result.md` | One-camera sequence and evidence limits |
| `docs/validation.md` | Supplied checks, historical analysis and unresolved risk |
| `data/publication-validation.json` | Recorded export test/reproduction result |
| `docs/credits.md`, `NOTICE`, `LICENSE` | Pinned sources, attribution and license boundaries |
| `src/offline_firmware.py` | OE parser, checksum, decoder, bounded LZ4, resource/string parsers |
| `src/resource_candidate.py` | Exact-stock gate, gap translation checks, candidate construction |
| `src/resource_package.py` | Pinned full-image gate and exact 0101 extraction |
| `tools/reproduce.py` | Public CLI and output-directory handling |
| `data/english_gap_translations.json` | 39 research-authored translations keyed by string ID |
| `tests/` | Synthetic/parser/CLI tests and two optional stock-dependent tests |
| `SHA256SUMS` | Per-file integrity for every other exported file |

The package is self-contained for parser tests and reproduction given the exact
external stock input. It is **not** a self-contained emulator research archive.
If prose, manifests and actual code disagree, report the discrepancy; do not
silently change gates or re-label a different output as this r01.

## 3. Artifact identity — mandatory gates

Hashes are SHA-256 of whole files, not decoded payloads.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official full E148/1.1 stock input | 90,832,896 | `9de5d77e1d290fa2ed4ebc7d75cee0ed490befbc89566722467d1d421d66d637` |
| Full r01 intermediate | 90,832,896 | `68f5d1e8f7c2ed7c64a238b0f9ccfb8446ae9c78117ed632df930c7f44e16ad5` |
| r01 resource-only package; owner-tested artifact | 12,582,912 | `82aebb31264c29ce64921f8cecdc8a431a780df6d281d14b5706a2f85dc602fc` |
| Stock resource-only reference | 12,582,912 | `ff68b7bf98b1f7ff90a69b0d46c1c3e2c68673021bbc94f93c7b39b196fdd2cf` |

The full r01 was not installed. The stock resource-only reference is not an
independent rescue loader. A matching public update file does not prove two
cameras have identical flash, factory settings or region policy. The official
app's downloaded bytes were not separately captured and hashed during the stock
update; the pinned file is the independently obtained offline reproduction input.

The CLI derives the full candidate in memory and writes nothing by default.
It verifies both full and extracted hashes. Changing a translation changes the
candidate; the current CLI should reject it. A new variant needs separate identity,
review and evidence, not a cosmetic replacement of the expected digest.

## 4. Exact layout and transformation

All numeric offsets in this section are file or decoded-payload offsets unless
explicitly called logical addresses. They are not physical flash block addresses
and are not device write instructions.

### 4.1 Container

`parse_container(data, expected_model=b'\x14\x80')` reads concatenated OE
components with 32-byte header, encoded payload, and 32-byte trailer. It checks
OE magic, native model bytes, positive 16-byte-aligned payload length, bounds,
matching header/trailer fields, zero header checksum field, unique component types,
and the modulo-2^32 sum of little-endian words in header + decoded payload + trailer.
Encoding uses the pinned 16-byte permutation and byte inversion; it is not a
cryptographic authenticity check. `verify_stock` first requires exact full size
and hash. Component order is `[0100, 0101, 0106, 010e, 0102]` (hexadecimal types).

| 0101 field | Expected value |
|---|---|
| Full-file component offset | 24,903,680 bytes |
| Component logical address | `0x42140000` |
| Decoded payload origin | `0x42140020` |
| Decoded payload length | 12,582,848 bytes |
| Header + payload + trailer | 12,582,912 bytes |
| Component version field | `0x0100`, even in official full 1.1 |

Do not interpret the 0101 component's version field as proof of firmware 1.0.
The full-bundle digest is the build gate.

### 4.2 Resources and strings

- Resource descriptors are 16 bytes: source address, span, two flag words.
  The parser checks the directory boundary, zero flags, ranges and overlaps.
  It returns 38 nonempty records for this input.
- Compressed records use the `olycompress` wrapper and bounded LZ4 decoding.
  This decoder is a host extraction aid; its acceptance is not a proof of native
  loader stream compatibility. r01 appends uncompressed strings.
- English string record: **5**; Japanese string record: **10**;
  original Japanese font record: **28**.
- Japanese decoded font SHA-256:
  `7fc31c0938eadd3bbfe0d9120078dd6861de0cec53bfa6996dc6a9b1c64505f5`.
- String load base: `0xa407f540`; **4,909** pointers. UTF-16LE text is before
  the pointer table. The first eight bytes hold absolute table start/end addresses;
  subtract the load base to obtain record-relative offsets. Bounds, alignment,
  count and termination are checked.
- Copy the complete original English text area and pointer table. In the new
  table, 4,870 pointer values stay unchanged and 39 gap-entry pointers are replaced;
  the original English resource itself remains byte-for-byte unchanged. Determine
  exactly the IDs that are JP-nonempty / EN-empty. The translation ID set must
  equal this set, not merely contain it.
- Append each gap translation and adjust only its pointer. Added characters must
  be printable ASCII or CR/LF; no NUL. Preserve the ordered `@hhhh@` icon escapes,
  dollar controls and leading-dollar status of the original Japanese entry.
  Reject stray `@` escapes. Ordinary glyph checks do not prove line layout.
- Keep the Japanese 148-byte font metadata tail: two 74-byte descriptors, first
  empty, second naming `OlympusLanguage_jpntft`; trailing original padding must
  be zero. The existing font resource remains untouched.
- Align the new string resource to 512 bytes. Its length is **318,464** bytes,
  below native capacity **392,192** (`0x5fc00`); headroom **73,728** bytes.

### 4.3 Only allowed changes for r01

1. Verify the maximum end of the existing resource records is decoded offset
   `0x8871e0` (one of the 38 records ends there) and the remaining reserve is zero-filled.
2. Write the 318,464-byte new string resource into that reserve. New source
   logical address is `0x429c7200`; source and span are 512-byte aligned.
3. At decoded payload offset `0xa0` (record 10), replace exactly eight bytes:
   `001e4842001c0300` → `00729c4200dc0400` (source and span). The rewritten field
   is eight bytes wide; four byte values actually differ.
4. Recompute the 0101 trailer's final four checksum bytes, encode, and reparse.
5. Verify every other resource record, every component header, and every
   non-resource component is unchanged. A witness applying just the two
   decoded-range edits must equal the candidate payload.
6. Require the pinned full-r01 digest, extract only 0101, reparse that one-component
   package and require its pinned digest. Compare stock reference separately.

`make_candidate(stock, translations)` returns `(full_bytes, patches, strings,
expected_strings)`. `extract_resource_package(full, variant)` accepts only
`'stock'` or `'candidate'`. `tools/reproduce.py:build` returns artifact bytes plus
a manifest. The original JP strings remain stored but descriptor 10 selects the
new table. Some labels/context may still refer to the Japanese slot.

## 5. Reproduction without hardware

Requirements: Python **3.9+**, standard library only. The recorded export run used
Python **3.9.13**; other platforms/interpreters were not all independently tested.
Run commands from the package root. The repository does not fetch firmware.
Acquire the official target input separately, preserving its original bytes,
and compare its whole-file SHA-256 with section 3.

```sh
python -B -m unittest discover -s tests -v
python -B tools/reproduce.py --stock /path/to/OLY_E_148_1100_0000_0000.BIN
```

Without `OM5_TEST_STOCK`, the recorded suite ran 41 tests: **39 passed, 2 skipped**.
Skipping the two integration tests is expected and is not evidence of successful
firmware reconstruction. With the exact external input, **41/41 passed**.

```powershell
$env:OM5_TEST_STOCK='D:\firmware\stock.BIN'
python -B -m unittest discover -s tests -v
```

```sh
OM5_TEST_STOCK=/path/to/stock.BIN python -B -m unittest discover -s tests -v
```

The CLI checks that the stock path names an ordinary file with the exact expected
size before opening, repeats the type/size check on the open handle, and bounds
the read to the expected size plus one byte. The subsequent full-hash check remains
mandatory. These checks are not an operating-system sandbox or a guarantee against
all concurrent filesystem changes.

The CLI's default prints JSON including hashes, string sizes/count, patch-range
hashes, `device_access: false`, `hardware_safety_proven: false`, `files_written: 0`.
Exit 0 means offline reproduction matched; handled validation/I/O errors return
exit 2 and `Refused: ...` on stderr. Neither exit code grants installation approval.

Optional explicit writes:

```sh
python -B tools/reproduce.py --stock /path/to/stock.BIN --output-dir /path/to/new-research-output
```

The directory must be new and its parent must exist. Its final name cannot be
`DCOLYMP` or `OMKIT` (case-insensitive). Outputs are first written exclusively as
`.partial` files under a `.INCOMPLETE` subdirectory, flushed, synced, closed and
verified by disk size/SHA-256. Only after all three pass are they renamed into the
output root; the empty `.INCOMPLETE` directory is removed last. Final files are:
`JP_EN_resources.research-bin`, `STOCK_resources.research-bin`, `build.json`.
The full candidate is not written. No updater filenames, device transport,
network requests, SD enumeration or installation are implemented.

**Path checks are not a device sandbox**: a user can point the output option at
a removable volume or an unsuitable ancestor. Choose an ordinary local research
directory explicitly, outside the checkout and publication archive. An I/O error
can leave an explicitly incomplete set. A failure during final renames can leave
some fully verified files at the root alongside `.INCOMPLETE`; the multi-file
operation is not a filesystem transaction. Do not treat that directory as a
successful result or retry over it. Inspect it and choose a fresh directory for
another offline run. Disk readback is not camera-flash readback.

Common refusal causes: other firmware version/model, partial input, corrupted
bytes, edited translations, unknown layout, nonzero reserve, changed font,
malformed control tokens or an existing output directory. Stop and investigate
the cause. Do not bypass guards to make an unfamiliar file pass.

## 6. Evidence ledger

Use these labels in further reports:

| Label | Meaning in this package |
|---|---|
| `observed` | Locally checked bytes, code behavior, tests or hashes |
| `owner_report` | Camera state described by its human operator |
| `source_report` | Upstream documentation or another researcher's result |
| `inference` | Reasoned conclusion whose premises must be stated |
| `unknown` | Not established; retain null/unknown rather than inventing a pass |

### Directly reproduced in the export

- Pinned full input gate; candidate and stock resource hashes; exact extraction.
- Synthetic checks for truncation, malformed headers, model/checksum/duplicate
  components, bounds/overlaps, LZ4 failures, string pointers, translation set,
  metadata/tokens, native size bound and output-directory refusal.
- Two optional integration tests include actual rebuild/slices and rejection of
  wrong-build, wrong-model and partial-package input.

### Historical research summarized, not reproducible from this export alone

- Six independent AI-assisted review rounds: binary, updater/loader,
  startup/resource dependence, UI readiness, writer/indicators, single-trial procedure.
- Independent Caduceus encoder reconstruction matched the same candidate bytes.
- Original research test suite: 32 passed. This is a different suite from the
  portable export's 41 tests; do not add them together as unique coverage.
- OM-Emu native lookup across all 4,909 string IDs, selected menu/help paths,
  resource-loader and updater-worker experiments. Synthetic settings,
  substituted resource reads and modeled peripherals limited the experiments.
  Some startup/UI paths were unresolved for stock as well as candidate.
- With controller operations replaced by host RAM, stock and r01 selected
  logical range `[0x42140000, 0x42d40000)`, erasing all 12 MiB before writing.
  Modeled erase failures stopped programming. When lower functions falsely
  signaled success, upper-worker fixtures could accept discarded programming or
  corrupt readback. This is a limit of the modeled upper checks, not an observed
  physical-controller failure. Physical block mapping and ECC were not measured.
- Native success/error indicator configurations differ. Actual physical waveforms
  and recovery after damaged 0101 were not independently established.

Raw harnesses/logs and original private reports are intentionally outside this
public package. Cite those claims as historical project reports and state the
reproduction gap; do not invent files or assert that the package reruns them.

### One physical camera, owner-operated

1. Camera identified as OM-5MarkII. Official OI.Share update 1.0 → 1.1 and settings
   restoration completed; app again reported model/version after restart.
2. Before the custom trial, owner confirmed baseline RAW/JPEG, video/playback,
   AF/IBIS, rear screen/EVF and Japanese menus.
3. Exact resource-only r01, chosen card and a reviewed single-trial procedure
   were specifically authorized with acknowledged loss/recovery risk. File
   identity was checked after card eject/reinsert.
4. Owner performed the SD updater sequence and reported steady light, then
   blinking. Later normal power-on without the update card produced English
   menus, according to the owner. The lamp report alone was not flash readback.
5. Owner removed the update file; its absence was verified locally.
6. Owner reported a partial functional pass without identifying every tested item.

The one-trial authorization was consumed. No additional installation, downgrade,
rescue, factory-data operation or arbitrary device probe is authorized by this
history. No independent screen recording, flash dump, factory-data comparison,
long-term evaluation or destructive recovery experiment was performed.

## 7. Remaining work, ordered by value

1. Independently reproduce using the exact stock input; report code revision,
   Python/OS, input/output hashes, checks run and any skips. Keep firmware private.
2. Review the 39 additions for meaning, icon/control order, wording and layout.
   Identify entries by ID. Font coverage alone is not layout validation.
3. Collect a specific ordinary-use checklist from the owner of the already-tested
   body: all tabs/help, RAW/JPEG, video/playback, AF/IBIS, display/EVF, sleep/wake,
   two normal restarts. Never infer a check from the broad partial-pass statement.
4. Investigate native startup and recovery dependencies offline. Document every
   stub/substitution and unresolved peripheral/other-CPU input. Distinguish logical
   component addresses from physical flash mapping. Never test by cutting power
   or damaging resources on a working camera.
5. If proposing a changed variant, create a separate profile and review its input,
   diff, strings, build digest, tests and residual risk before a hardware proposal.

On any model/build/hash/bounds/checksum/parser mismatch, stop dependent work and
report exact non-sensitive evidence. Do not silently repair or auto-retry a device.
Never treat existing read-only/reproduction access as permission to flash, change
region/settings, install a loader, issue unknown USB/PTP commands, or touch
bootloader, factory calibration, OTP/fuses or serial data.

## 8. Upstream, publication and privacy

Pinned upstream commits and their roles are in `docs/credits.md`. The relevant
projects are OMKit (`necrostaz/omkit`), native Caduceus (`xulfr/caduceus-om5`),
db firmware (`azqeurio/om-c-firmware`), OM-Emu (`flatpanda/om-emu`) and OM Firmware
Atlas. The separate `tadejs/caduceus-om5` target must not be confused with E148.
The closed db patcher was never executed for this research and did not generate
r01. Its localization claims and inspected recipes were research leads.

Original code/docs here use Apache-2.0; upstream and separately supplied firmware
retain their own terms. See `LICENSE` and `NOTICE`. Attribution is not endorsement.
No upstream maintainer review is implied by the independent AI-assisted review.

Share source, hashes, synthetic tests, scoped findings and proposed corrections.
Do not attach firmware, fonts, full decoded vendor tables, personal paths,
account/card/network identifiers, serial numbers, credentials or full chats.
Inspect screenshots/EXIF and logs before publication. Do not contact maintainers,
publish a repository or submit issues without authorization from the current user.

Suggested report format for a future agent:

```text
Scope / revision:
Exact model + build + input digest:
What I directly checked:
Commands + environment + output hashes:
Pass / fail / skip and limitations:
Findings with file/function or byte-range evidence:
Owner reports / upstream claims used separately:
Unknowns and next offline step:
Device actions: none [or explicit authorized action + its evidence]
```

Keep the final conclusion proportionate: **one owner-reported English boot,
partial functional acceptance, reproducible bytes, unresolved recovery**.
