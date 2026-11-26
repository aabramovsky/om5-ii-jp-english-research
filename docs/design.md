# Design of resource-only r01

All offsets and addresses below belong to the pinned E148/1.1 file or analyzed
runtime code. They are not instructions for arbitrary writes to a camera.

## Container and language resources

The full stock bundle has components 0100, 0101, 0106, 010e and 0102. Component 0101
starts at file offset 24,903,680 and has logical address `0x42140000`; its decoded
payload starts at `0x42140020`. Header plus payload plus trailer occupy 12,582,912
bytes. Its component version field is `0x0100` even inside the official 1.1 bundle;
the exact full-bundle digest is the build identity gate.

There are 38 nonempty resource records. The Japanese string record is index 10
and its font is record 28. Existing English strings are record 5. Each language
has 4,909 string pointers; text precedes its pointer table.

## Transformation

1. Verify the complete stock input's size and SHA-256, component layout,
   checksums, resource bounds and exact Japanese font hash.
2. Keep the original English resource unchanged. Copy its text and pointer table
   into the new resource; only the 39 gap-entry pointers are then replaced.
   Identify the exact set of
   Japanese-nonempty/English-empty entries and require the translation mapping
   to cover that set and no other IDs.
3. Append those 39 research translations, preserving ordered icon escapes
   (`@hhhh@`) and dollar controls. Reject malformed controls and unsupported
   added glyphs. Keep the original Japanese 148-byte font descriptor tail.
4. Put the resulting 318,464-byte string resource in verified zero-filled reserve
   at decoded payload offset `0x8871e0`, source address `0x429c7200`.
5. At decoded offset `0xa0`, change only the eight source/span bytes of the
   Japanese descriptor: `001e4842001c0300` -> `00729c4200dc0400`.
6. Recompute the 0101 trailer checksum, encode, independently reparse, and verify
   that all other component bytes and all other resource records are unchanged.
7. Require the exact full-r01 digest and extract only 0101. Require the exact
   resource-only digest before any output is created.

The new resource span is below the native string-buffer capacity of 392,192
bytes, leaving 73,728 bytes. The new source and span are 512-byte aligned. The
unchanged Japanese font contains the ordinary glyphs used by the candidate;
this does not prove every line fits every UI layout.

## Translation provenance

`data/english_gap_translations.json` contains only the 39 research-authored gap
translations, not the vendor's full English/Japanese tables. They are not official
OMDS translations. Their reachability, wording and layout require further review.

The original Japanese strings remain in the component, but record 10 selects the
new table. Language labels may still reflect the Japanese slot in some contexts.
Region policy itself was neither decoded nor rewritten on the physical camera.
