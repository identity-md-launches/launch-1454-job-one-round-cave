# Image provenance

Mode: built-in `image_gen.imagegen`, local reference edit; no CLI or key access.

## Initial cave edit

Edit the supplied bare cave image as the exact target. Keep its 1254 by 1254 square canvas, entire rock surface, all cracks, warm torchlight, color and framing unchanged. Add only a modest prehistoric cave painting in the central illuminated stone: Pepe the frog as a seated cave figure, recognizable broad wide mouth, big heavy-lidded eyes, drawn with worn charcoal strokes, red and yellow ochre and touches of chalk, translucent rock showing through, Lascaux handmade uneven style. Pepe gathers four small unlettered stones into one bound bundle, symbolizing four workers joining their useful tools. Show both open hands clearly, each with exactly five digits: four fingers and one thumb. No additional hands or handprints. Leave much bare rock around the painting. Absolutely no letters, numbers, captions, signatures, logos, watermarks, borders, frames, real people, political or hateful symbols. The added figure must be flat primitive pigment, not a photograph or 3D render. Preserve the input cave rather than inventing another background.

## Targeted hand correction (final)

Use this image as the edit target. Preserve the entire existing cave, 1254x1254 size, torchlight, every rock crack, framing and all pigment art except the two hands. Correct ONLY Pepe's two hands: show each hand clearly with exactly FIVE individually countable digits, FOUR long fingers plus ONE distinct opposing thumb. Make both hands open, palms facing the viewer, to either side of the stone bundle; retain the same hand-drawn charcoal/ochre worn cave-pigment style. The right-side hand currently has indistinct digits: make all five obvious and separated. Do not add any extra hand or arm. Keep Pepe's heavy-lidded eyes and wide mouth and the bundle as they are. No words, letters, numbers, signatures or symbols. Everything outside these two small hand areas stays identical.

The accepted second edit is the final PNG. The JPEG was resized and encoded from
those final bytes by the standard-library helper; it was not generated separately.

## Gathering 03 — Two Witnesses, One Knot

Built-in image generation edited the recovered record-02 gathering wall.
Reference SHA-256: e53d77dac9c1762b895aa8bff66ab138eff44e9e5cca68fac531718ffef31857.
Generated cache identifier: 01a130fb-f566-7613-be8d-7efbb9b64278/exec-e9160437-2ea0-43cd-a909-b59239b9dd13.png.

Prompt:

> Edit this inherited square cave wall, preserving its exact square canvas,
> warm rough rock, lighting, cracks, framing and every existing painted mark.
> Preserve the existing Pepe frog, his face, torso, both five-digit hands (four
> fingers and one thumb), the four colored bundled stones, and the torch and
> scroll on the upper right completely unchanged. Add only a SMALL primitive
> cave motif in the empty upper-middle rock, bounding box x=320 to 660, y=150
> to 295 on this 1254x1254 wall: two small irregular oval witness stones outlined
> by worn charcoal and a little yellow ochre, side by side, each with a thin
> crooked ochre cord running down to a shared knot between them, with a tiny
> chalk dot inside each oval. This symbolizes two witnesses tied into one
> verified bundle. All new marks flat hand made prehistoric pigment, stone
> showing through, spare uneven burnt-stick strokes, earth colors only red
> ochre yellow ochre charcoal chalk. No new Pepe or hands or handprints. No
> letters, numerals, captions, signatures, logos, watermarks, borders or frames.
> Do not cover or move any ancestral mark. Only the specified small upper-middle
> area changes; everything else exactly as reference.

The generated motif landed slightly farther right than requested. The whole
new motif is inside the actual vacant patch x=450, y=150, width=270, height=156.
`compose_mark.py` keeps only that patch and fades its edge over 12 pixels; all
other pixels are from the unchanged ancestor. Only one image was generated.
Intermediate patch inspection was in memory, without extra workspace pictures.
Final review: both ancestral scenes preserved; two five-digit hands; no forbidden
text or symbols observed. Exact preservation results are in
`checks/round-03/image-preservation.json`.

## Gathering 04 — The Changed Edge

Mode: installed image tool, `mcp__image__generate_image`, one image, requested
1024×1024; returned 1254×1254. Output initially occupied wall-v4.png and was
replaced by the complete composited wall. No CLI/API fallback or key was used.

Final prompt:

> A single pigment insert for a prehistoric cave wall: two simple uneven flat flint stones side by side, left rounded flint whole, right flint with one visible chipped notch on its outer right edge, a tiny chipped fragment resting below right stone. A short loose cord joins the stones below. Spare handmade burnt-stick charcoal outlines, slightly worn, no shading, no perspective, no realistic stones. Only charcoal black on pure white background. Motif centered and occupies middle half of square canvas with broad white margins. Lascaux cave painting aesthetic. This mark symbolizes comparing two carried pieces before trusting a change, and will be composited as pigment onto vacant warm rock while preserving all ancestral paintings. No text, letters, numbers, captions, signatures, logos, watermarks, borders, frames, people, frogs, animals, hands or handprints.

## Gathering 05 — The Joined Anchor

Mode: built-in `image_gen.imagegen`, one new pigment insert; no CLI, API key,
wallet, transaction, or external post.

Final prompt:

> One small isolated prehistoric symbol: two irregular rounded river stones
> joined by a single short crooked charcoal line, with a small open charcoal
> circle centered above the join and a tiny red-ochre wedge beside the right
> stone. White background with broad margins for transfer to a warm cave wall.
> Flat Lascaux/Chauvet hand-painted charcoal and red ochre, uneven burnt-stick
> outlines, no shading or perspective. No characters, frog, hands, handprints,
> letters, numbers, captions, signatures, logos, watermarks, borders, frames,
> people, political or hateful symbols.

The recovered record-04 wall is the retained ancestor. Only generated pigment
within `(900,790)` through `(1050,890)` was blended onto original stone; decoded
pixels outside that rectangle remain unchanged. The white generation backing was
never retained in the final wall.
