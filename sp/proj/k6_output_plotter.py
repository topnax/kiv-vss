from dateutil import parser
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime
import json
import sys


def load_data(file_name):
    data = {}
    with open(file_name, "r") as f:
        for line in f.readlines():
            line_data = json.loads(line)
            if line_data["type"] == "Point":
                metric = line_data["metric"]
                metric_data = data.get(metric, [])
                metric_data.append((line_data["data"]["value"], parser.parse(line_data["data"]["time"])))
                data[metric] = metric_data
    return data

def get_metric_data(data, watched_metric):
    metric_data = data[watched_metric]

    return ([time for (value, time) in metric_data], [value for (value, time) in metric_data])


def process_file(file_name):
    data = load_data(file_name)
    
    for (metric, metric_data) in data.items():
        print(f"type: {metric}, length: {len(metric_data)}")

    watched_metric = "http_req_waiting"

    http_req_data = get_metric_data(data, watched_metric)
    vus_data = get_metric_data(data, "vus")

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Time")
    ax1.set_ylabel(watched_metric)

    plot_1 = ax1.plot(http_req_data[0], http_req_data[1], color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("VUs", color="green")
    plot_2 = ax2.plot(vus_data[0], vus_data[1], color="green")
    ax2.tick_params(axis="y", labelcolor="green")


    #plt.plot(metric_times, metric_values)
    plt.gcf().autofmt_xdate()
    plt.show()

    #plt.plot(metric_times, metric_values)
    #plt.gcf().autofmt_xdate()
    #plt.show()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        process_file(sys.argv[1])
    else:
        print("Specify a file to be processed")

