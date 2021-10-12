import math

from histogram import print_histogram
from poisson import PoisonDistribution
import random


def test_distribution():
    pd = PoisonDistribution(6)

    histogram = {}

    n = 1000
    for _ in range(n):
        while True:
            x = random.randint(0, 100)
            y = random.uniform(0, 1)
            p = pd.pdf(x)
            if y <= p:
                # print(f"{x},{y},{p}")
                histogram[x] = histogram.get(x, 0) + 1
                break

    print_histogram(histogram)


if __name__ == "__main__":
    test_distribution()
