def expected_value(histogram):
    total = sum(histogram.values())
    return sum(map(lambda item: (item[0] / total) * item[1], histogram.items()))


if __name__ == "__main__":
    h = {
       1: 1,
       2: 1,
       3: 1,
       4: 1,
       5: 1,
       6: 1,
    }
    assert expected_value(h) == 3.5
