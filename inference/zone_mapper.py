"""Maps detection bounding boxes (in 640×640 YOLO input space) to face zone labels."""

_ZONES = ("forehead", "nose", "left_cheek", "right_cheek", "chin")


def map_bbox_to_zone(bbox: list[float], image_width: int, image_height: int) -> str:
    """Return zone label for a detection bbox [cx, cy, w, h] in pixel coords.

    Zones assume the subject fills most of the image (standard selfie framing):
      forehead   — top 25 % of height
      chin       — bottom 25 % of height
      nose       — middle vertical band (25–55 %) AND centre horizontal third (30–70 %)
      left_cheek — middle vertical band, left 40 % (image-left = subject's right in mirrored selfie)
      right_cheek— middle vertical band, right 40 %
    """
    cx, cy = bbox[0], bbox[1]
    rel_x = cx / image_width
    rel_y = cy / image_height

    if rel_y < 0.25:
        return "forehead"
    if rel_y >= 0.75:
        return "chin"
    # Middle vertical band
    if 0.30 <= rel_x <= 0.70:
        if rel_y < 0.55:
            return "nose"
        # Lower centre → chin area already captured above, treat as nose
        return "nose"
    if rel_x < 0.30:
        return "left_cheek"
    return "right_cheek"
