def xyxy_to_xywh(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float, float]:
    return x1, y1, x2 - x1, y2 - y1


def xywh_to_xyxy(x: float, y: float, w: float, h: float) -> tuple[float, float, float, float]:
    return x, y, x + w, y + h


def clamp_bbox(
    x: float, y: float, w: float, h: float, img_w: int, img_h: int
) -> tuple[float, float, float, float]:
    x = max(0.0, min(x, float(img_w)))
    y = max(0.0, min(y, float(img_h)))
    w = min(w, float(img_w) - x)
    h = min(h, float(img_h) - y)
    return x, y, w, h


def compute_iou(box_a: tuple[float, ...], box_b: tuple[float, ...]) -> float:
    """Compute IoU between two boxes in xyxy format."""
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])

    inter = max(0.0, xb - xa) * max(0.0, yb - ya)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - inter

    if union <= 0:
        return 0.0
    return inter / union
