# Validation and limitations

## Checks supplied in this export

Synthetic tests cover container truncation, model/checksum/header rejection,
duplicate components, bounds and overlaps, LZ4 length/back-reference failures,
UTF-16 pointer tables, exact input gates, native string capacity, translation
coverage, font metadata and special-token preservation. They require no firmware.

Optional integration tests rebuild from the exact separately supplied stock file,
check both resource-only hashes and component boundaries, and reject wrong-build,
wrong-model and partial-package inputs. The offline CLI refuses existing output
directories, bounds its exact-size regular-file input read, and verifies all
expected hashes before output creation. Staged output is closed and checked by
disk size/SHA-256 before final names appear. Failure leaves an explicit
`.INCOMPLETE` set. Synthetic regressions exercise mid-write disk-full and corrupt
readback; multi-file finalization is not a filesystem transaction.

See `data/publication-validation.json` for the actual export validation results.
Generated firmware and test outputs are not included in this repository/archive.

## Earlier research checks

Before the physical attempt, six independent AI-assisted review rounds examined
binary integrity, native updater/loader behavior, startup/resource dependence,
UI readiness, the writer/indicator boundaries and the single-trial procedure.
The original research suite passed 32 tests with its available exact inputs.
The candidate was independently reconstructed with the pinned Caduceus encoder
and matched byte-for-byte. Those historical checks are separate from the
portable export's test run.

OM-Emu executed native string lookup for all 4,909 IDs and selected menu/help
paths. Native resource-loader and updater-worker experiments were also performed.
Emulator coverage depended on synthetic settings, resource-read substitutions
and modeled peripherals; it was not a complete camera boot or sensor simulation.
Some UI/startup paths remained unresolved on both stock and candidate.

The historical emulator harnesses and raw logs are not bundled here. This export
reproduces the transformation and parser tests, not the entire earlier emulator
environment. The most relevant remaining questions are listed below so others
can independently investigate them.

## Writer and recovery findings

With controller operations replaced by host RAM, stock and r01 used the same
logical `[0x42140000, 0x42d40000)` range. The updater erased all 12 MiB before
programming. Erase-error cases prevented programming in the modeled path.

Negative fixtures also showed that the upper worker could accept discarded
programming or corrupted readback if lower functions falsely returned success.
This demonstrates a limit of the upper-layer check, not that real hardware
silently corrupts data; controller behavior, physical blocks and ECC were not
modeled or measured.

Success/error indicator driver configurations differed in native code. Their
physical waveforms on this body were not independently measured. Startup analysis
remained blocked on other-CPU/peripheral data absent from the update file.
Availability of the SD updater after a damaged 0101 resource remains unknown.

## Useful next contributions

- Independently reproduce the pinned output from the pinned stock input.
- Review the 39 non-vendor gap translations and their token/layout requirements.
- Report clearly scoped UI and ordinary-function observations on this exact body/build.
- Investigate startup/resource/recovery dependencies offline with explicit stand-ins.

No destructive power-interruption testing, factory-data manipulation, unknown
device commands or blind retries were used or are requested by this project.
