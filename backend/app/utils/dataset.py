import random
from pathlib import Path

from app.utils.image import SUPPORTED_IMAGE_EXTS


def list_images_in_dir(dir_path: Path) -> list[Path]:
    if not dir_path.exists():
        return []
    return [f for f in dir_path.rglob("*") if f.suffix.lower() in SUPPORTED_IMAGE_EXTS]


def split_dataset(
    image_paths: list[Path],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, list[Path]]:
    """Split image paths into train/val/test sets."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

    rng = random.Random(seed)
    shuffled = list(image_paths)
    rng.shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    return {
        "train": shuffled[:train_end],
        "val": shuffled[train_end:val_end],
        "test": shuffled[val_end:],
    }
