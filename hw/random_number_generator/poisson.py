import math
import random
import sys


class PoisonDistribution:

    def __init__(self, rate, precision=1000000, e=0.000000001):
        self.rate = rate
        self.pdf_cache = {}
        self.cdf_cache = {}
        self.cdf_inv_cache = {}
        self.precision = precision
        self.initialize(e)

    def cdf(self, n):
        # calculate the CDF by summing previous PDFs
        if n in self.cdf_cache:
           return self.cdf_cache[n]
        cdf = sum([self.pdf(k) for k in range(0, n)])

        # store the calculated CDF to the cache
        self.cdf_cache[n] = cdf
        # floor the CDF value (to increase the chance of utilising it) before storing it to the inverted CDF cache
        self.cdf_inv_cache[self.floor(cdf)] = n
        return cdf

    def floor(self, v):
        # floor a value using the precision set in the attribute
        return math.floor(v * self.precision) / self.precision

    def cdf_inv(self, v):
        # floor the value to be looked up in order to increase the chance of cache utilization
        v_floor = self.floor(v)

        # check whether value present in the cache
        if v_floor in self.cdf_inv_cache:
            return self.cdf_inv_cache[v_floor]

        # initialize variables before finding inverse CDF value
        min_diff = sys.float_info.max
        min_diff_value = 0
        for value, n in self.cdf_inv_cache.items():
            # compute difference between the desired value and the actual value stored in the cache
            diff = abs(value - v_floor)
            if diff < min_diff:
                # better match found, update variables
                min_diff = diff
                min_diff_value = value

        # key of the value found, fetch it from the cache
        return self.cdf_inv_cache[min_diff_value]

    def pdf(self, k):
        # check whether the desired PDF value was already calculated
        if k in self.pdf_cache:
            return self.pdf_cache[k]
        # value not present in the cache, we have to calculate it
        pdf = self.pdf_calc(k)

        # update the cache
        self.pdf_cache[k] = pdf
        return pdf

    def pdf_calc(self, k):
        # poisson PDF definition
        return ((self.rate ** k) * math.exp(-self.rate)) / math.factorial(k)

    def initialize(self, e):
        # initialize the generator by generating initial values INV CDF values
        diff = 1
        last_cdf = 0
        n = 1
        # compute CDF values till the lambda * 2.5 values generated or till the difference
        # before the current cdf and the previous one is smaller than a certain constant
        while n < self.rate * 2.5 or diff > e:
            cdf = self.cdf(n)
            diff = abs(last_cdf - cdf)
            last_cdf = cdf
            n += 1

    def rand(self):
        return self.cdf_inv(random.uniform(0, 1))
