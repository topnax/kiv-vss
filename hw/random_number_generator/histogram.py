import math

HISTOGRAM_VALUE_DECIMAL_PLACES = 2
HISTOGRAM_FREQUENCY_MAX_CHARS = 100
HISTOGRAM_COLUMN_SYMBOL = "*"


def print_histogram_item(value, frequency, max_key_label_length):
    # format the histogram item key and justify it
    label = format_histogram_key(value).ljust(max_key_label_length, " ")
    
    # generate column based on the given frequency
    column = frequency * HISTOGRAM_COLUMN_SYMBOL

    # assemble the output
    output = f"{label} | {column}"

    print(output)


def format_histogram_key(value):
    return '{0:.2f}'.format(value)


def print_histogram(histogram):
    # determine the maximum frequency
    max_value_label_length = len(format_histogram_key(max(histogram.keys())))

    # determine max and min histogram values in order to be able to scale the histogram output
    max_freq = max(histogram.values())
    min_freq = min(histogram.values())
    for value in sorted(histogram.keys()):
        frequency = histogram[value]
        # scale the frequency based on min/max hist. freq
        frequency = math.floor(((min_freq+frequency)/max_freq)*HISTOGRAM_FREQUENCY_MAX_CHARS) + 1
        print_histogram_item(value, frequency, max_value_label_length)


if __name__ == "__main__":
    print_histogram({
        0.676767: 2,
        0.7: 5,
        1.99: 5,
        12.99: 7,
        13: 100,
        14: 40
    })
