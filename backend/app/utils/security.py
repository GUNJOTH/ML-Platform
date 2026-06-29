from pathlib import Path


def sanitize_filename(filename: str, fallback: str) -> str:
    cleaned = filename.replace("\\", "/").split("/")[-1].strip()
    return cleaned or fallback
