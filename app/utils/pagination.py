from __future__ import annotations

import math


def page_count(total: int, page_size: int) -> int:
    return max(1, math.ceil(total / page_size))
