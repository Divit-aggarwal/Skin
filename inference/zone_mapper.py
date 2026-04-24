"""Maps detection bounding boxes to face zone labels.

Implemented in Slice 5. Zones: forehead, nose, left_cheek, right_cheek, chin.
"""


def map_bbox_to_zone(
    bbox: list[float], image_width: int, image_height: int
) -> str:
    raise NotImplementedError("Zone mapping implemented in Slice 5")
