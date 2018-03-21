#! /usr/bin/env python3
# EEG power classifier and visualizer
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

from sklearn.neighbors import KNeighborsClassifier
from analysis import run_analysis, plot
from matplotlib import pyplot

import numpy as np
import argparse
import os

# Global variable because it is hard to pass on argument with function pointer
KNN = None

def on_click(event):
    x = event.xdata
    y = event.ydata
    if x is None or y is None or KNN is None:
        return

    prediction = KNN.predict([[x, y]])
    print("{} {}:\t{}".format(x, y, prediction))


def create_knn_classifier(results, labels):
    """ Create a KNN classifier """
    # List of data points
    X = []
    # List of corresponding labels
    Y = []
    # The first label
    i = 0

    # Transform the format of the data to one readable by K-Nearest-Neighbors (KNN)
    for result in labels:
        data = np.transpose(np.array(results[result]))
        data = [[line[0], line[1]] for line in data]
        X += data
        Y += [i] * len(data)
        # Create a new label for the next condition
        i += 1

    # Create the KNN model and fit on the data
    KNN = KNeighborsClassifier(n_neighbors=7)
    KNN.fit(X, Y)

    return KNN


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize eeg readings using \
    python scatterplots. The script uses folders as a representation of \
    conditions. Every folder must contain two channels, c1.mat and c2.mat. ')
    # Specify folder
    parser.add_argument('folder', nargs='+', help='Select folders to \
    compare. Each folder must contain both a c1.mat and \
    c2.mat.')
    # Specify sample rate
    parser.add_argument('-s', '--sample_rate', help='Specify the sample rate \
    of the measurement', type=int, default=256)
    # Specify frequency range
    parser.add_argument('-b', '--band', nargs=2, type=int, help="Specify the \
    frequency band in Hz, for example \'--band 8 13\'", default=[8, 13])
    # Specify the length of the signal in seconds
    parser.add_argument('-l', '--length', type=float, help="Specify the \
    length of the signal to process, for example \'--length 1.5\' to only \
    process the first one and a half seconds of the signal. If the specified \
    length is longer than the length of the signal, the whole signal is used.")

    args = parser.parse_args()
    folders = args.folder
    band = args.band
    sample_rate = args.sample_rate
    length = args.length

    results = run_analysis(folders, band, sample_rate, length)
    KNN = create_knn_classifier(results)

    # Create an interactive plot
    plot(results, sample_rate, band, callback=on_click)
    exit(0)
