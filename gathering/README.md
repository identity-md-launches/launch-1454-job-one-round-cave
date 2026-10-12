# The Changed Edge — Gathering 04

Handoff revision joins the lines' archive and unsigned-transaction comparisons.
Two joined flints, one chipped, represent checking a change before carrying it
onward. REPORT.md records every line's trials, results and remaining gaps;
COINS.md says none because all tools work with existing ZTO/IMD or offline.

## Outputs and checks

- `artifacts/gathering/wall-v4.png`: required output, 1254×1254, 8-bit RGB PNG.
- `artifacts/gathering/wall.png`: byte-identical continuing gathering wall.
- `dist/gathering/04.jpg`: 512×512 baseline color JPEG, 67,724 bytes.
- `dist/gathering/04.json`: prescribed six-trait record, actual PNG SHA-256 URL.
- `dist/goals.json`: exact four line goals; `dist/index.html`: all 117 records.
- `shared/handoff-revision/`: portable standard-library Python kit with provenance.

Offline checks passed: 147 line tests, 34 inherited shared tests, 13 new shared
checks, nine inherited regressions and all offline demos. Native Line 2 inspected
and source-checked the actual 73,901-byte shared package. A copied standalone kit
ran without line folders. Fresh real ZTO PublicNode observations and the failed
HTTP-429 two-provider trial are retained in `checks/round-04/`.

```sh
python3 -B shared/handoff-revision/revision.py demo
python3 -B shared/handoff-revision/test_revision.py
python3 -B gathering/check_deliverable.py
```

`run_checks.py` reruns the 26 reviewed offline commands, saving bounded receipts.
`build_gallery.py` rebuilds exact goals and gallery; `make_thumbnail.py` rebuilds
only this round's JPEG. All delivered worker tools use only the standard library.
No dependency installation, remote imports or submodules were added.

## Image production and visual review

The local gathering wall was absent. The last painted record, 03, was recovered
from its artifact URL and checked against its SHA-256:
`dceafc14303f22e203ee0ba20b812094d33ed9c2d0bd7575a1af182b90456f0e`.
Placeholder bare-cave URLs were not used. The assignment's installed image
creation tool generated a charcoal pigment insert at the required output path.
The insert was inspected, then overwritten with the finished whole wall.
No additional picture or preview was saved in the workspace.

`compose_mark_v4.py` cropped the motif in memory, removed white, and transferred
only worn charcoal pigment to vacant rock at x=260, y=270, width=165, height=110.
The original stone shows through. Decoded RGB comparison found **2,388 changed
pixels and zero changed pixels outside that rectangle**. All earlier marks,
Pepe, bundled stones, torch, scroll, rock cracks, torchlight, dimensions and
framing remain unchanged. No ancestor was erased, moved or redrawn.

The full PNG and actual JPEG were visually inspected. Pepe retains his wide
mouth and big heavy-lidded eyes. Both inherited hands were counted as **four
fingers and one thumb, five digits each**. No new hands or handprints were added.
The flints have uneven, worn charcoal outlines and bare stone interiors. No
letters, numbers, captions, signatures, logos, watermarks, borders, frames,
real people, political or hateful symbols were observed.

Unmet visual requirements: **none identified on inspection**. Limitations:
manual review is not independent artistic certification. Inherited naturalistic
rock texture is preserved, with flat pigment marks. The small new motif is
intentionally restrained and may require viewing the full wall to see its chip.
The tool requested 1024×1024 for the insert but returned 1254×1254; its native
size was decoded before compositing. The final wall preserves the ancestor's
1254×1254 dimensions. The JPEG is reduced from that final wall, never separately
generated. Final PNG SHA-256:
`23821808be606f6f8ea922f2e1457be6d8af17050aec08d9088b98113ec027d6`.

Imagegen prompt and tool mode are recorded in IMAGE-PROMPTS.md. The composition
script requires the original record-03 wall plus the generated insert and
refuses an already-finished wall, preventing accidental repainting.

## Scope

No line source, record or thumbnail was changed. Records 01–03 remain unchanged;
record 04 replaces its existing placeholder. This is a later gathering, so
placeholders were preserved rather than reseeded. The final named PNG output
remains untracked for the daemon's upload. The structural checker validates
formats, hashes, gallery order, size limits, current provenance and unchanged
line files. It does not certify behavior, provider truth or visual quality.

## The Joined Anchor — Gathering 05

`shared/anchor-bridge/` is the new portable standard-library glue: it links a
Line 1 block-pinned snapshot to a Line 4 validated transfer window only when
both close at exactly the same block hash and height. Its demo and five offline
tests passed. The full line audit is in `REPORT.md`; `COINS.md` records **none**.

- `artifacts/gathering/wall-v5.png` and `artifacts/gathering/wall.png` are
  byte-identical, **1254×1254**, 8-bit RGB PNG files.
- `dist/gathering/05.jpg` is a **512×512**, baseline, three-component JPEG,
  67,800 bytes.
- `dist/gathering/05.json` has the required six traits and actual SHA-256 image
  URL. `dist/goals.json` and `dist/index.html` were rebuilt locally.

The built-in image generator made one white-backed pigment insert of two
unlettered stones joined beneath an open ring with a small red-ochre wedge.
`compose_mark_v5.py` removed its white background in memory and applied only
pigment within `(900,790)`, 150×100, on recovered record-04 stone. The decoded
comparison found 6,661 changed pixels and **zero** changes outside that rectangle.
`make_thumbnail_v5.py` encoded the JPEG from final wall bytes only.

Manual review of final PNG and JPEG found inherited Pepe still has the wide mouth
and heavy-lidded eyes, with two visible hands of four fingers plus one thumb each;
the new motif adds no hand or handprint. Warm rough rock, framing, cracks,
torchlight and prior pigment marks remain. No letters, numbers, captions,
signatures, logos, watermarks, borders, frames, real people, political/hateful
symbols, photographs, or 3D rendering were found. **Unmet visual requirements:
none identified in this local review.** This review is not an independent artistic
certification; generated pigment inside the declared patch is approximate and the
small mark can soften in the JPEG.
