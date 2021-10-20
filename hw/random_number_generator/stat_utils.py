import math


def expected_value(histogram):
    total = sum(histogram.values())
    return sum([value * frequency / total for value, frequency in histogram.items()])


def variance(histogram):
    ev = expected_value(histogram)
    total = sum(histogram.values())
    return sum([((value - ev) ** 2) * (frequency / total) for value, frequency in histogram.items()])


def standard_deviation(histogram):
    return math.sqrt(expected_value({k ** 2: v for (k, v) in histogram.items()}) - expected_value(histogram) ** 2)


def test_stat_utils():
    h = {
        0: 0.2,
        1: 0.45,
        2: 0.15,
        3: 0.2
    }
    assert expected_value(h) == 1.350
    assert variance(h) == 1.0275
    assert math.isclose(standard_deviation(h), 1.0136567466)


if __name__ == "__main__":
    test_stat_utils()
