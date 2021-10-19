import math
import random
import sys


class PoisonDistribution:

    def __init__(self, rate, e=0.000000001):
        self.rate = rate
        self.pmf_cache = {}
        self.cdf_cache = {}
        self.cdf_inv_cache = {}
        self.initialize(e)

    def cdf(self, n):
        # calculate the CDF by summing previous PMFs
        if n in self.cdf_cache:
            return self.cdf_cache[n]

        # compute CDF by summing over PMF values
        cdf = sum([self.pmf(k) for k in range(0, n + 1)])

        # store the calculated CDF to the cache
        self.cdf_cache[n] = cdf
        self.cdf_inv_cache[cdf] = n
        return cdf

    def cdf_inv(self, x):
        # check whether value present in the cache
        if x in self.cdf_inv_cache:
            return self.cdf_inv_cache[x]

        # initialize variables before finding inverse CDF value
        min_diff = sys.float_info.max
        min_diff_value = 0
        for value in self.cdf_inv_cache.keys():
            if value >= x:
                min_diff_value = value
                break

        # key of the value found, fetch it from the cache
        return self.cdf_inv_cache[min_diff_value]

    def pmf(self, k):
        # check whether the desired PMF value was already calculated
        if k in self.pmf_cache:
            return self.pmf_cache[k]
        # value not present in the cache, we have to calculate it
        pmf = self.pmf_calc(k)

        # update the cache
        self.pmf_cache[k] = pmf
        return pmf

    def pmf_calc(self, k):
        # poisson pmf definition
        return ((self.rate ** k) * math.exp(-self.rate)) / math.factorial(k)

    def initialize(self, e):
        # initialize the generator by generating initial values INV CDF values
        diff = 1
        last_cdf = 0
        n = 0
        # compute CDF values till the lambda * 2.5 values generated or till the difference
        # before the current cdf and the previous one is smaller than a certain constant
        while n < self.rate * 2.5 or diff > e:
            cdf = self.cdf(n)
            diff = abs(last_cdf - cdf)
            last_cdf = cdf
            n += 1

    def rand(self):
        return self.cdf_inv(random.uniform(0, 1))

    def rand_knuth(self):
        l = math.exp(-self.rate)
        p = 1.0
        k = 0
        while True:
            k += 1
            p *= random.uniform(0, 1)
            if p <= l:
                break
        return k - 1

    def expected_value(self):
        return self.rate

    def variance(self):
        return self.rate


def test_poisson_distribution():
    pd = PoisonDistribution(2.5)
    for x in range(0, 5):
        print(f"#{x} cdf:{pd.cdf(x)}, pmf:{pd.pmf(x)}")


if __name__ == "__main__":
    test_poisson_distribution()
