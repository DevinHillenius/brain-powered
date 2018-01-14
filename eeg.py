#! /usr/bin/env python3

import mne
import sys
import math
import numpy as np
from scipy.io import loadmat

from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score

from mne.decoding import CSP
from matplotlib import pyplot


def fourrier(data, sample_rate):
    """ Perfom a fourrier analysis, returns a 2 by n matrix. """
    timestep = 1.0/sample_rate
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


def experiment(c1, c2, sample_rate, band):
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
    mat = np.transpose(mat)
    # Remove redundant channel dimension
    mat = mat[:, 0, :]
    return mat

if __name__ == "__main__":
    if len(sys.argv) > 2:
        # load two channels of two conditions
        cond1_c1 = load_eeg_mat(sys.argv[1]) 
        cond1_c2 = load_eeg_mat(sys.argv[2])
        
        cond2_c1 = load_eeg_mat(sys.argv[3]) 
        cond2_c2 = load_eeg_mat(sys.argv[4])

        # samples per second
        sample_rate = 256
        alpha = (8, 13)
        delta = (1, 3)
        beta = (14, 20)
        band = alpha

        res1 = experiment(cond1_c1, cond1_c2, sample_rate, band)
        res2 = experiment(cond2_c1, cond2_c2, sample_rate, band)
        pyplot.scatter(res1[0], res1[1])
        pyplot.scatter(res2[0], res2[1])
        axes = pyplot.gca()

        axes.set_xlim([min(res1[0] + res2[0]), max(res1[0] + res2[0])])
        axes.set_ylim([min(res1[0] + res2[1]), max(res1[0] + res2[1])])
        pyplot.show()
    else:
        print("Usage: ./eeg.py [condition 1 channel 1] [condition 1 channel 2]\
 [condition 2 channel 1] [condition 2 channel 2]")
