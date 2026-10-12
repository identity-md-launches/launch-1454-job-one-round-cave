#!/usr/bin/env python3
"""Encode gathering 05's 512px JPEG from the final wall without another image."""
from pathlib import Path
from make_thumbnail import jpeg, png_rgb, resize


def main():
    width, height, rows = png_rgb(Path("artifacts/gathering/wall.png").read_bytes())
    if (width, height) != (1254, 1254):
        raise ValueError("expected the 1254px gathering wall")
    encoded = jpeg(resize(width, height, rows))
    if len(encoded) >= 100_000:
        raise ValueError("JPEG exceeds 100 KB")
    target = Path("dist/gathering/05.jpg")
    target.write_bytes(encoded)
    print(f"{target}: 512x512 baseline JPEG, {len(encoded)} bytes")


if __name__ == "__main__":
    main()
