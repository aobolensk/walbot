import importlib
from typing import Any

import numpy as np

from src.log import log


def optional_numba_jit(func) -> Any:
    try:
        numba = importlib.import_module("numba")
    except Exception as e:
        log.warning(
            f"Function {func.__name__} is missing numba package for better performance! "
            "Error details:")
        log.warning(f" - numba import error: {e}")
        return func
    return numba.njit(fastmath=True)(func)


@optional_numba_jit
def levenshtein_distance(a: str, b: str):
    """
    Calculates Levenshtein distance between two strings using dynamic programming.
    Complexity: O(len(a) * len(b))
    """
    m = len(a)
    n = len(b)
    d = np.zeros((m + 1, n + 1), dtype=np.uintc)
    for i in range(m + 1):
        d[i, 0] = i
    for j in range(n + 1):
        d[0, j] = j
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + int(a[i - 1] != b[j - 1]))
    return d[m, n]


def precompile_algs() -> None:
    log.debug("Started precompiling functions...")
    levenshtein_distance("", "")
    log.debug("Finished precompiling functions")
