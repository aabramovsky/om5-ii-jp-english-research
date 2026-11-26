# Sources, credits and provenance

This experiment builds on other researchers' work. Their tools and reports were
essential inputs; none of these maintainers has reviewed or endorsed this public
export merely by being credited here.

| Project | Pinned revision used in the research | Contribution |
|---|---|---|
| [OMKit](https://github.com/necrostaz/omkit) | `a29db07f4cab2f9f9688462975ffa510b4d6fd97` | Native E148/1.1 research, container reference, SD updater description and limits |
| [Caduceus for OM-5 / xulfr](https://github.com/xulfr/caduceus-om5) | `1357ef68b73df6c3636795f5a21d353fb8774110` | Resource/container references and independent encoder used to cross-check r01 |
| [db firmware / azqeurio](https://github.com/azqeurio/om-c-firmware) | `036763267140bb418286d88b6dccb6246d91d7f7` | Localization lead and statically inspected resource recipes; closed patcher not executed |
| [OM Firmware Atlas](https://github.com/xulfr/om-firmware-atlas) | `bd8aacf41f761cf52e2408e0273ea862bfdd3a46` | Model/version separation, source discovery and evidence standards |
| [OM-Emu](https://github.com/flatpanda/om-emu) | `cafd92d94126006b3099e360f188bc2bf5493c31` | Native-code execution and UI/resource experiments with documented stand-ins |

The independent Caduceus `tools/oly_container.py` used during research had SHA-256
`bca685b207370c8802c69aff7b4ef2326789ce22fce7a7bc39315e8079928e4e`.
Its format lineage credits [cakelesscoder/caduceus-ep7](https://github.com/cakelesscoder/caduceus-ep7)
and [androidfanman/caduceus-om3](https://github.com/androidfanman/caduceus-om3).

OMKit software and Caduceus use Apache-2.0. OMKit's documentation/data have their
own CC-BY-4.0 terms; this export contains original summaries and source links,
not their documentation, artwork or bundled data. Other upstream projects retain
their own licenses; their repositories, executables and firmware outputs are not
included in this export. See LICENSE and NOTICE for this package.

The native E148 work above is distinct from the
[tadejs port for the original OM-5](https://github.com/tadejs/caduceus-om5).
No compatibility with E144 or a cross-model port is claimed.

Manufacturer references:
- [OM-5 Mark II support](https://explore.omsystem.com/us/en/om-5-mark-ii-support)
- [Official OI.Share update procedure](https://support.jp.omsystem.com/jp/support/cs/qa/content/007267/index.html)
- [Japanese-market language FAQ](https://support.jp.omsystem.com/jp/support/cs/qa/content/007437/index.html)
