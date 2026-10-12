#!/usr/bin/env python3
"""Add only the generated joined-anchor pigment to the recovered gathering wall."""
import hashlib
import json
from pathlib import Path
import struct
import zlib

from make_thumbnail import png_rgb

SOURCE_SHA256 = "23821808be606f6f8ea922f2e1457be6d8af17050aec08d9088b98113ec027d6"
INSERT = Path("/tmp/pepeolithic-gathering/joined-anchor-insert.png")
LEFT, TOP, WIDTH, HEIGHT = 900, 790, 150, 100


def encode_png(width, height, rows):
    def chunk(tag, content):
        body = tag + content
        return struct.pack(">I", len(content)) + body + struct.pack(">I", zlib.crc32(body))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(
        ">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
        chunk(b"IDAT", zlib.compress(b"".join(b"\0" + bytes(row) for row in rows), 9)) +
        chunk(b"IEND", b""))


def main():
    source = Path("/tmp/pepeolithic-gathering/gathering-v4.png").read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError("recovered record-04 wall hash does not match")
    width, height, rows = png_rgb(source)
    if (width, height) != (1254, 1254):
        raise ValueError("unexpected ancestor dimensions")
    insert_width, insert_height, insert_rows = png_rgb(INSERT.read_bytes())
    # The deliberately white generated background contributes no pigment. Keep
    # only dark charcoal or saturated ochre pixels, preserving the wall stone.
    points = []
    for y, row in enumerate(insert_rows):
        for x in range(insert_width):
            red, green, blue = row[3*x:3*x+3]
            if min(red, green, blue) < 150 or (red > green * 1.25 and red > blue * 1.45):
                points.append((x, y))
    if not points:
        raise ValueError("generated insert has no pigment")
    x0, x1 = min(x for x, _ in points) - 3, max(x for x, _ in points) + 4
    y0, y1 = min(y for _, y in points) - 3, max(y for _, y in points) + 4
    if not (0 <= x0 < x1 <= insert_width and 0 <= y0 < y1 <= insert_height):
        raise ValueError("generated insert crop escapes canvas")
    result = [bytearray(row) for row in rows]
    changed = 0
    for y in range(HEIGHT):
        source_y = y0 + y * (y1-y0) // HEIGHT
        for x in range(WIDTH):
            source_x = x0 + x * (x1-x0) // WIDTH
            red, green, blue = insert_rows[source_y][3*source_x:3*source_x+3]
            darkness = max(0.0, min(1.0, (238 - min(red, green, blue)) / 220))
            ochre = max(0.0, min(1.0, (red - max(green, blue) * 1.12) / 120))
            opacity = max(darkness * .70, ochre * .62)
            if opacity == 0:
                continue
            pigment = (112, 54, 25) if ochre > darkness else (38, 27, 17)
            index = 3 * (LEFT+x)
            old = rows[TOP+y][index:index+3]
            new = bytes(round(value*(1-opacity) + paint*opacity)
                        for value, paint in zip(old, pigment))
            result[TOP+y][index:index+3] = new
            changed += new != old
    outside = sum(rows[y][3*x:3*x+3] != result[y][3*x:3*x+3]
                  for y in range(height) for x in range(width)
                  if not (LEFT <= x < LEFT+WIDTH and TOP <= y < TOP+HEIGHT))
    if changed < 250 or outside:
        raise ValueError("unexpected pigment transfer extent")
    encoded = encode_png(width, height, result)
    target_dir = Path("artifacts/gathering")
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "wall.png").write_bytes(encoded)
    (target_dir / "wall-v5.png").write_bytes(encoded)
    receipt = {"source_sha256": SOURCE_SHA256,
               "wall_sha256": hashlib.sha256(encoded).hexdigest(),
               "rectangle": {"x": LEFT, "y": TOP, "width": WIDTH, "height": HEIGHT},
               "changed_pixels": changed, "changed_pixels_outside_rectangle": outside,
               "dimensions": [width, height], "format": "8-bit RGB PNG",
               "method": "Generated pigment was composited only within the declared vacant-rock rectangle."}
    Path("gathering/checks/round-05").mkdir(parents=True, exist_ok=True)
    Path("gathering/checks/round-05/image-preservation.json").write_text(
        json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
