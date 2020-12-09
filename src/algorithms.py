import numpy as np


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
    for j in range(n + 1):
        for i in range(m + 1):
            d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + int(a[i-1] != b[j-1]))
    return d[m, n]
