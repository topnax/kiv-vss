import math


class PoisonDistribution:

    def __init__(self, rate):
        self.rate = rate

    def pdf(self, k):
        return ((self.rate ** k) * math.exp(-self.rate)) / math.factorial(k)
