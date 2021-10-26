import math


def expected_value(histogram, total=None):
    if total is None:
        total = sum(histogram.values())
    return sum([value * frequency for value, frequency in histogram.items()]) / total


def variance(histogram, ev=None, total=None):
    if ev is None:
        ev = expected_value(histogram)
    if total is None:
        total = sum(histogram.values())
    return sum([((value - ev) ** 2) * (frequency) for value, frequency in histogram.items()]) / total


def standard_deviation(histogram, ev=None):
    if ev is None:
        ev = expected_value(histogram)
    return math.sqrt(expected_value({k ** 2: v for (k, v) in histogram.items()}) - expected_value(histogram) ** 2)


def test_stat_utils():
    h = {
        0: 0.2,
        1: 0.45,
        2: 0.15,
        3: 0.2
    }
    total = sum(h.values())
    ev = expected_value(h, total) 
    assert ev == 1.350
    assert variance(h, ev, total) == 1.0275
    assert math.isclose(standard_deviation(h), 1.0136567466)


if __name__ == "__main__":
    test_stat_utils()
