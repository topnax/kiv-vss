from histogram import print_histogram
from poisson import PoisonDistribution


def test_distribution(distribution):
    histogram = {}

    n = 100000
    for _ in range(n):
        p = distribution.rand()
        histogram[p] = histogram.get(p, 0) + 1

    print_histogram(histogram)


if __name__ == "__main__":
    test_distribution(PoisonDistribution(10))
