"""Orchestrates acne, wrinkle, and oiliness models into a single score response.

Score formula (Slice 5 implementation):
  overall = acne * 0.4 + wrinkle * 0.3 + oiliness * 0.3
  severity: < 33 → mild, 33–66 → moderate, > 66 → severe
"""

import numpy as np


def run_pipeline(image_array: np.ndarray) -> dict:
    """Run all models and return aggregated scores. Implemented in Slice 5."""
    raise NotImplementedError("ML pipeline implemented in Slice 5")
