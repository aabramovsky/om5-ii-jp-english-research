# One-camera report: 26 November 2026

## Scope

- Native OM-5 Mark II / E148, Japanese-market body.
- Official firmware 1.0 was first updated to 1.1 through OM Image Share.
- After the official update and settings restore, the application reported
  OM-5MarkII / 1.1. The owner confirmed the requested baseline functions and
  Japanese stock menus before the custom attempt.
- Exactly one resource-only r01 attempt was explicitly authorized and performed.
  No full-r01 image or OMKit loader was installed for this experiment.

## Evidence

| Observation | Evidence type |
|---|---|
| Exact source, output size and SHA-256 match | Locally verified |
| Same removable card and file hash after safe eject/reinsert | Locally verified |
| Fully charged battery, camera off, USB disconnected before attempt | Owner report |
| Front lamp first steady, then blinking | Owner report |
| Normal power-on after removing the update card | Owner report |
| English menus after that normal boot | Owner report |
| Subsequent partial functional check found no issue | Owner report; checked subset unspecified |
| Update file removed; card no longer contained it | Locally verified after owner removal |

The physical sequence followed the previously reviewed single-trial procedure
based on the [pinned OMKit SD updater description](https://github.com/necrostaz/omkit/blob/a29db07f4cab2f9f9688462975ffa510b4d6fd97/docs/platform/om5m2/fw1100/install.md#4-install-the-loader-patch).
This is a historical report, not a general installation recommendation. The
reviewed r01 single-trial procedure is not included in this export. The linked
OMKit section describes its own loader installation, not a recipe to apply r01.
The
steady-to-blinking sequence was treated as the reported completion indication,
not independent proof of a correct flash write.

## What remains unverified

The post-install checklist requested RAW/JPEG capture, video, playback, AF/IBIS,
rear display/EVF, all menu tabs and help, sleep/wake and two full power cycles.
The owner reported only a partial pass, without specifying the completed subset.
Do not mark individual items or the whole checklist as passed from that answer.

There was no independent recording of the physical screen, flash dump/readback,
factory-data comparison or failed-resource recovery test. The local official
stock hash identifies the reproduction input; the firmware bytes downloaded
internally by OI.Share were not separately extracted and hashed.

One successful boot supports feasibility on this body and does not establish
general compatibility, complete English UI coverage or long-term reliability.
Device/account/card identifiers and exact local timestamps are intentionally
omitted. No serial number is needed to reproduce the software result.
