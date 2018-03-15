#! /usr/bin/env python3
# EEG power analysis and vizualiser
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

from scipy.io import loadmat
from matplotlib import pyplot
import numpy as np
import argparse
import sys
import math
import os

VERBOSE = False

def fourrier(data, sample_rate):
    """ Perfom a fourrier analysis, returns a 2 by n matrix. """
    timestep = 1.0/float(sample_rate)
    power = np.absolute(np.fft.fft(data)) / data.shape[0]
    frequency = np.fft.fftfreq(data.shape[0], d=timestep)

    return np.column_stack((frequency, power))


def bandpass(spectrum, band):
    """ Sample frequency, lower frequency bound, higher frequency bound."""
    new_spectrum = []
    for entry in spectrum:
        if (entry[0] > band[0] and entry[0] < band[1]):
            new_spectrum.append(entry)
    return np.array(new_spectrum)


def spectrum_meanpower(spectrum):
    """ Calculate the mean power of a spectrum. """
    return np.mean(spectrum[:, -1], axis=0)


def trial_meanpower(data, sample_rate, band):
    """ Calculate the mean power of a trial. """
    f = fourrier(data, sample_rate)
    b = bandpass(f, band)
    return spectrum_meanpower(b)


def analysis(c1, c2, sample_rate=256, band=[8, 13], length=1):
    """ Perform a mean power analysis over the signal """
    if length != None and length > 0:
        c1 = c1[:round(sample_rate*length)]
        c2 = c2[:round(sample_rate*length)]

    results = [[], []]
    for trial in c1:
        results[0].append(trial_meanpower(trial, sample_rate, band))
    for trial in c2:
        results[1].append(trial_meanpower(trial, sample_rate, band))
    return results


def load_eeg_mat(path, label='data'):
    """ Load the eeg data into a numpy 2D matrix where
        the shape is (#trials, #datapoints)"""
    # Load matrix (# datapoints, # channels,  # tests)
    mat = loadmat(path)[label]
    if VERBOSE:
        print("Input Format: {}".format(mat))

    if len(mat.shape) == 3:
        mat = np.transpose(mat)
        # Remove redundant channel dimension
        mat = mat[:, 0, :]

    if VERBOSE:
        print("Loaded {}".format(path))
        print("Number of trials: {}".format(mat.shape[0]))
        print("Length of trials: {}\n".format(mat.shape[1]))
        print("Output Format: {}".format(mat))
    return mat

def run_analysis(folders, band, sample_rate, length):
    """ Run an analysis over the specified eeg recordings using the specified
        parameters. """
    results = {}
    for folder in folders:
        p1 = os.path.join(folder, 'c1.mat')
        p2 = os.path.join(folder, 'c2.mat')
        if not os.path.isfile(p1) or not os.path.isfile(p2):
            print("Error: c1.mat and c2.mat could not be found in the" +
                  "specified folders.  Please check if the directories and " +
                  "files are present.")
            exit()
        c1 = load_eeg_mat(p1)
        c2 = load_eeg_mat(p2)
        exp = analysis(c1, c2, sample_rate, band, length)
        results[folder] = exp
        if VERBOSE:
            print("Final analysis format: {}".format(results))
    return results

def plot(results, sample_rate=256, band=(8,13), callback=None):
    """ Plot the results of the analyis to the screen. """
    legend_entries = []

    for result in results:
        legend_entries += pyplot.plot(results[result][0], results[result][1], 'o', label=result)
    pyplot.legend(handles=legend_entries)

    pyplot.xlabel("Mean power First Channel")
    pyplot.ylabel("Mean power Second Channel")
    fig = pyplot.gcf()
    fig.canvas.set_window_title("Brain Powered: Sample rate: {}/s, \
    Band: {}-{}Hz".format(sample_rate, band[0], band[1]))

    # Add an optional button press callback to the plot
    if callback:
        fig.canvas.mpl_connect('button_press_event', callback)
    pyplot.show()

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

    parser.add_argument('-l', '--length', type=float, help="Specify the \
    length of the signal to process, for example \'--length 1.5\' to only \
    process the first one and a half seconds of the signal. If the specified \
    length is longer than the length of the signal, the whole signal is used.")

    parser.add_argument('-v', dest='verbose', action='store_true', help='Enable verbose output for debugging purposes')
    args = parser.parse_args()

    folders = args.folder
    band = args.band
    sample_rate = args.sample_rate
    length = args.length
    VERBOSE = args.verbose

    results = run_analysis(folders, band, sample_rate, length)
    plot(results, sample_rate, band)
    exit(0)
