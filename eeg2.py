#! /usr/bin/env python3

import mne
import sys
import numpy as np

from scipy.io import loadmat
from scipy.signal import butter, lfilter, welch
from sklearn.neighbors import KNeighborsClassifier

FREQUENCY_SAMPLING = 256

def butter_bandpass(lowcut, highcut, order=4):
    nyq = 0.5 * FREQUENCY_SAMPLING
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut):
    b, a = butter_bandpass(lowcut, highcut)
    y = lfilter(b, a, data)
    return y


def load_eeg_mat(path, label='data'):
    """ Load the eeg data into a numpy 3D matrix where the shape is
         (# datapoints, # channels,  # tests) """
    return loadmat(path)[label]


def combine_channels(c1, c2):
    """ Combine data from the two channels together in a 3D matrix where
        the shape is (# tests, # channels, # datapoints) """
    return np.concatenate((np.transpose(c1), np.transpose(c2)), axis=1)

def tm(data):
    data = []
    for trail in cond1_c2.T:
        data.append(np.mean(trail.T))

    return data

def create_classifier_matrices(c1ch1, c1ch2, size1, c2ch1, c2ch2, size2):
    cond1 = np.column_stack((c1ch1, c1ch2))
    cond2 = np.column_stack((c2ch1, c2ch2))
    X = np.concatenate((cond1, cond2), axis=0)
    y = np.concatenate((np.zeros(size1), np.ones(size2)))
    print(X)
    print(y)
    return X, y

if __name__ == "__main__":
    if len(sys.argv) > 2:
        cond1_c1 = load_eeg_mat(sys.argv[1] + "/c1_cond.mat")
        cond1_c2 = load_eeg_mat(sys.argv[1] + "/c2_cond.mat")

        cond2_c1 = load_eeg_mat(sys.argv[2] + "/c1_cond.mat")
        cond2_c2 = load_eeg_mat(sys.argv[2] + "/c2_cond.mat")

        c1c1 = tm(cond1_c1)
        c1c2 = tm(cond1_c2)
        c2c1 = tm(cond2_c1)
        c2c2 = tm(cond2_c2)

        classifier = KNeighborsClassifier(n_neighbors=2)
        X, y = create_classifier_matrices(c1c1[:20], c1c2[:20], 20,
                                          c2c1[:20], c2c2[:20], 20)
        classifier.fit(X, y)
        X, y = create_classifier_matrices(c1c1[20:], c1c2[20:], len(c1c2[20:]),
                                          c2c1[20:], c2c2[20:], len(c2c2[20:]))
        print(classifier.score(X, y))

        # print(cond1_c1.shape)

        # print(welch(butter_bandpass_filter(cond1_c1, 8, 13), FREQUENCY_SAMPLING, nperseg=33)[1].shape)

    else:
        print("Usage: python eeg.py [folder1] [folder2]")
