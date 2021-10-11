HISTOGRAM_VALUE_DECIMAL_PLACES = 2
HISTOGRAM_FREQUENCY_MAX_CHARS = 40
HISTOGRAM_COLUMN_SYMBOL = "*"


def print_histogram_item(value, frequency, max_value_label_length):
    label = format_histogram_value(value)
    label = label.ljust(max_value_label_length, " ")

    if frequency > HISTOGRAM_FREQUENCY_MAX_CHARS:
        frequency_str = f"({frequency})"
        column = frequency_str + " " + \
                 HISTOGRAM_COLUMN_SYMBOL * (HISTOGRAM_FREQUENCY_MAX_CHARS - len(frequency_str) - 1)
    else:
        column = HISTOGRAM_COLUMN_SYMBOL * frequency

    output = f"{label}: {column}"

    print(output)


def format_histogram_value(value):
    return '{0:.2f}'.format(value)


def print_histogram(histogram):
    max_value_label_length = len(format_histogram_value(max(histogram.values())))

    for value, frequency in histogram.items():
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
