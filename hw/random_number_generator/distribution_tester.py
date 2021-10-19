import sys

from stat_utils import expected_value, variance
from histogram import print_histogram
from poisson import PoisonDistribution


def test_distribution(distribution, n):
    histogram = {}

    for _ in range(n):
        p = distribution.rand()
        histogram[p] = histogram.get(p, 0) + 1

    print(f"E_teorie={distribution.expected_value()}")
    print(f"D_teorie={distribution.variance()}")
    print(f"E_vypocet={expected_value(histogram)}")
    print(f"D_vypocet={variance(histogram)}")
    print()
    print("HISTOGRAM")
    print_histogram(histogram)


def test_histogram():
    if len(sys.argv) == 3:
        test_distribution(PoisonDistribution(float(sys.argv[2])), int(sys.argv[1]))
    else:
        for (i, (rate, sample)) in enumerate([(5, 10000), (9, 100000)]):
            title = f"Default test case #{i + 1} rate={rate}, n={sample}"
            print(title)
            print("-" * len(title))
            test_distribution(PoisonDistribution(rate), sample)
            print()


if __name__ == "__main__":
    test_histogram()
