from pathlib import Path

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def is_image_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_IMAGE_EXTS


def get_image_dimensions(content: bytes) -> tuple[int, int]:
    """Parse image dimensions from raw bytes (supports JPEG/PNG)."""
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        w = int.from_bytes(content[16:20], "big")
        h = int.from_bytes(content[20:24], "big")
        return w, h

    if content[:2] == b"\xff\xd8":
        i = 2
        while i < len(content) - 1:
            if content[i] != 0xFF:
                break
            marker = content[i + 1]
            if marker in (0xC0, 0xC2):
                h = int.from_bytes(content[i + 5 : i + 7], "big")
                w = int.from_bytes(content[i + 7 : i + 9], "big")
                return w, h
            length = int.from_bytes(content[i + 2 : i + 4], "big")
            i += 2 + length

    return 0, 0
