"""Stage the 18 November 2026 front page for the judge.

The picture itself is the entry: it already lives in this repository as
``entry.png``.  All this program does is carry those exact bytes to the
place the harness reads, ``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output``
when the variable is unset), after proving the file is really a PNG
and fits the 1 MiB cap.  No network, no randomness, no drawing here --
run it twice and the two outputs are byte for byte the same.
"""

import os
import struct
import sys
from pathlib import Path

FRONT_PAGE = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
BYTE_LIMIT = 1_048_576
PAGE_WIDTH = 1024
PAGE_HEIGHT = 1024


def front_page_path() -> Path:
    """The picture shipped beside this script."""
    return Path(__file__).resolve().parent / FRONT_PAGE


def read_ihdr_size(blob: bytes) -> tuple:
    """Pixel size from the PNG header chunk, or None when it is absent."""
    if len(blob) < 24 or blob[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def load_front_page() -> bytes:
    """Read the staged picture, refusing anything that is not a PNG."""
    picture = front_page_path()
    if not picture.is_file():
        raise SystemExit(f"front page missing: {picture}")
    blob = picture.read_bytes()
    if blob[:8] != PNG_MAGIC:
        raise SystemExit("front page is not a PNG file")
    if len(blob) > BYTE_LIMIT:
        raise SystemExit(f"front page too large: {len(blob)} bytes")
    size = read_ihdr_size(blob)
    if size is None:
        raise SystemExit("front page has no IHDR chunk")
    if size != (PAGE_WIDTH, PAGE_HEIGHT):
        raise SystemExit(f"front page is {size[0]}x{size[1]}, want 1024x1024")
    return blob


def publish(blob: bytes) -> Path:
    """Write the picture to the harness output directory."""
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / FRONT_PAGE
    dest.write_bytes(blob)
    if dest.read_bytes() != blob:
        raise SystemExit("published copy does not match the front page")
    return dest


def main() -> int:
    blob = load_front_page()
    dest = publish(blob)
    print(f"front page staged: {len(blob)} bytes -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
