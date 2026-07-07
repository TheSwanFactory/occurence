"""Settlement-channel diagnostics."""

from __future__ import annotations

import numpy as np

from topographo.core.algebra import CayleyDicksonAlgebra


def average_metric_operator(algebra: CayleyDicksonAlgebra, events: np.ndarray) -> np.ndarray:
    """Return the finite-sample average of M_z = L_z.T L_z."""
    if len(events) == 0:
        raise ValueError("events must be non-empty")
    return sum(algebra.metric_operator(event) for event in events) / len(events)
