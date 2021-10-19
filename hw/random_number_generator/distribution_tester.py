from expected_value import expected_value
from histogram import print_histogram
from poisson import PoisonDistribution


def test_distribution(distribution):
    histogram = {}

    n = 1000000
    for _ in range(n):
        p = distribution.rand()
        histogram[p] = histogram.get(p, 0) + 1

    print_histogram(histogram)

    print(f"Expected value: {expected_value(histogram)}")


if __name__ == "__main__":
    test_distribution(PoisonDistribution(5))
