# One-camera report: 26 November 2026

## Scope

- Native OM-5 Mark II / E148, Japanese-market body.
- Official firmware 1.0 was first updated to 1.1 through OM Image Share.
- After the official update and settings restore, the application reported
  OM-5MarkII / 1.1. The owner confirmed the requested baseline functions and
  Japanese stock menus before the custom attempt.
- Exactly one resource-only r01 attempt was explicitly authorized and performed.
  No full-r01 image or OMKit loader was installed for this experiment.

## Installation sequence used

This is the short account of what worked on this owner's camera. Read the entire
sequence, including button timing and stop conditions, before considering a repeat.
It concerns only native **OM-5 Mark II / E148 on official 1.1** and the exact
resource-only r01 below. Another model, version or modified baseline is not covered.

1. **Establish official 1.1.** Back up photographs and available camera settings.
   Use a manufacturer-supported update route that offers exactly 1.1, following
   its instructions; this owner used [OI.Share](https://support.jp.omsystem.com/jp/support/cs/qa/content/007267/index.html).
   [OM Workspace](https://explore.omsystem.com/us/en/firmware-update-instructions)
   is another official route where supported. Confirm 1.1 and normal operation
   afterward. A camera already on official 1.1 needs no repeat official update.
   If the official service offers a different version, this r01 procedure does
   not apply. The resource patch itself does not upgrade 1.0 to 1.1.
2. **Prepare the exact file and use the OK startup.** Reproduce the resource-only
   output using the [repository commands](../README.md#quick-start). The file used
   was `JP_EN_resources.research-bin`, **12,582,912 bytes**, SHA-256
   `82aebb31264c29ce64921f8cecdc8a431a780df6d281d14b5706a2f85dc602fc`.
   Copy those exact bytes to **`DCOLYMP/E1489999.BIN`**, with `DCOLYMP` at the root
   of a working camera-compatible SD card containing no needed files, OMKIT folder
   or other update file. Do not substitute the full intermediate or stock resource
   reference. Verify size and SHA-256 on the card, safely eject and reconnect it,
   verify again, then safely eject. With a fully charged battery, USB disconnected
   and the camera fully off, the owner inserted that card, held **OK**, and switched
   on. The front lamp was reported steady, then blinking. The pinned upstream guide
   describes a blank screen during this operation; a screen message saying OK is
   not the completion cue for this SD path.
3. **Return to ordinary use.** After the reported steady-to-blinking completion
   sequence, the owner released OK and switched the camera off. After full power-off,
   the update card was removed and the camera switched on normally, without OK.
   It booted with English menus. The update file was then deleted on the computer
   and its absence checked before the card was reused. Leaving the file on the
   card can trigger another update at a later OK-held startup. The owner's later
   assessment was that the camera works overall; every menu item has not been checked.

**OK-button timing, clarified by the owner:** OK was held continuously through the
steady light and blinking, including a couple of extra minutes of blinking while
waiting for the agent's reply. The owner released it only after receiving guidance.
This records the actual attempt, not a measured minimum hold time or a required
extra delay. The pinned upstream guide says to hold OK while switching on but does
not specify the earliest release moment. No shorter hold was tested here. A future
procedure should settle all operator actions before starting, not require waiting
for a live chat response during the update.

**Completion and stop conditions:** do not switch off, open a cover, remove the
card/battery or interrupt power during steady illumination or an unclear update
state. If the lamp sequence differs, its steady phase was missed, the camera starts
normally at the initial OK-held startup, or the outcome is otherwise unclear, do
not apply step 3 by guesswork or automatically retry. There is no timed battery-pull
instruction. Blinking alone is not proof of success; the subsequent normal boot
and English menus are separate owner observations. Resource writes can leave the
camera unbootable, and recovery after a damaged resource component is unproven.

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
| Later report: camera works overall; every menu item not checked | Owner report; not an exhaustive acceptance test |
| OK held through steady light and blinking, plus a couple of extra minutes awaiting guidance | Owner clarification; exact duration not measured |
| Update file removed; card no longer contained it | Locally verified after owner removal |

The physical sequence followed the previously reviewed single-trial procedure
based on the [pinned OMKit SD updater description](https://github.com/necrostaz/omkit/blob/a29db07f4cab2f9f9688462975ffa510b4d6fd97/docs/platform/om5m2/fw1100/install.md#4-install-the-loader-patch).
The short r01 account above is now included; the full internal review/approval
records are not. OMKit is credited for the updater entry mechanism, not as a
source of the r01 file or an endorsement. Its loader package was not installed.
The steady-to-blinking sequence was treated as the reported completion indication,
not independent proof of a correct flash write.

## What remains unverified

The post-install checklist requested RAW/JPEG capture, video, playback, AF/IBIS,
rear display/EVF, all menu tabs and help, sleep/wake and two full power cycles.
The first response was a partial pass without specifying the completed subset.
The later follow-up says the camera works overall, with every menu item not checked.
Neither statement identifies every tested function or completes the whole checklist.

There was no independent recording of the physical screen, flash dump/readback,
factory-data comparison or failed-resource recovery test. The local official
stock hash identifies the reproduction input; the firmware bytes downloaded
internally by OI.Share were not separately extracted and hashed.

One successful boot supports feasibility on this body and does not establish
general compatibility, complete English UI coverage or long-term reliability.
Device/account/card identifiers and exact local timestamps are intentionally
omitted. No serial number is needed to reproduce the software result.
