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

def nextpow2(in_list):
    output = []
    for entry in in_list:
        output.append(math.ceil(math.log(abs(entry), 2)))
    return output

def filter_jonas(data, channel, Fs, l1, u1):
    lb = l1 / 2
    ub = u1 / 2
    nfft = 2^nextpow2([data.shape[0]])[0]
    Y = np.fft.fft(data[:, channel], nfft) / data.shape[0]
    f = Fs / 2 * np.linspace(0, 1, nfft / 2 + 1)

    Ylb_1 = round(2 * lb * len(Y) / Fs ) + 1
    Ylb_2 = len(Y) - round(2 * lb * len(Y) / Fs) + 1
    Yhb_1 = round(2 * ub * len(Y) / Fs) + 1
    Yhb_2 = len(Y) - round(2 * ub * len(Y) / Fs) + 1

    Y[1:Ylb_1] = 0
    Y[Ylb_2:len(Y)] = 0
    Y[Yhb_1:int(len(Y) / 2)] = 0
    Y[int(len(Y) / 2):Yhb_2] = 0

    fY = np.fft.ifft(Y) * data.shape[0]
    fY = fY[1:len(data[:, channel])]

    Y2 = np.fft.fft(fY, nfft) / data.shape[0]
    selection = np.nonzero(f[l1:u1]) #?????
    return np.mean(2 * np.absolute(Y2[selection]))

def load_eeg_mat(path, label='data'):
    """ Load the eeg data into a numpy 3D matrix where the shape is
         (# datapoints, # channels,  # tests) """
    return loadmat(path)[label]


def load_measurement(folder_path):
    c1_base = load_eeg_mat(folder_path + "/c1_base.mat")
    c2_base = load_eeg_mat(folder_path + "/c2_base.mat")

    c1_cond = load_eeg_mat(folder_path + "/c1_cond.mat")
    c2_cond = load_eeg_mat(folder_path + "/c2_cond.mat")

    return (combine_channels(c1_base, c2_base),
            combine_channels(c1_cond, c2_cond))

def load_folders(folder1, folder2):
    cond1_c1 = load_eeg_mat(folder1 + "/c1_cond.mat")
    cond1_c2 = load_eeg_mat(folder1 + "/c2_cond.mat")

    cond2_c1 = load_eeg_mat(folder2 + "/c1_cond.mat")
    cond2_c2 = load_eeg_mat(folder2 + "/c2_cond.mat")

    return (combine_channels(cond1_c1, cond1_c2),
            combine_channels(cond2_c1, cond2_c2))

def combine_channels(c1, c2):
    """ Combine data from the two channels together in a 3D matrix where
        the shape is (# tests, # channels, # datapoints) """
    return np.concatenate((np.transpose(c1), np.transpose(c2)), axis=1)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        #base, cond = load_measurement(sys.argv[1])
        base, cond = load_folders(sys.argv[1], sys.argv[2])

        base_labels = np.zeros(base.shape[0])
        cond_labels = np.ones(cond.shape[0])

        # Input dimensions must be the same
        print(base.shape)
        print(cond.shape)

        #cond = np.resize(cond, base.shape, axis=2)
        print(base.shape)
        print(cond.shape)

        train_data = np.concatenate((base, cond))

        labels = np.concatenate((base_labels, cond_labels))
        print(labels)

        print(filter_jonas(base, 1, 256, 8, 13))

        # # Assemble a classifier
        # lda = LinearDiscriminantAnalysis()
        # csp = CSP(n_components=4, reg=None, log=True, norm_trace=False)
        #
        # # Use scikit-learn Pipeline with cross_val_score function
        # clf = Pipeline([('CSP', csp), ('LDA', lda)])
        # scores = cross_val_score(clf, train_data, labels, cv=ShuffleSplit(), n_jobs=1)
        # print(scores)
        #
        # # Printing the results
        # class_balance = np.mean(labels == labels[0])
        # class_balance = max(class_balance, 1. - class_balance)
        # print("Classification accuracy: %f / Chance level: %f" % (np.mean(scores),
        #                                                         class_balance))

        # data = load_eeg_mat(sys.argv[1])
        # # A single response in a trial
        # entry = np.transpose(data[:, :, 0])

        # # Not sure if we actually need this, we should be able to use the sklearn
        # # libraries with just the numpy matrices without the need to use MNE

        # # The second argument, sample frequency, is not the real sample frequency
        # info = mne.create_info(["Channel 1"], 10, 'eeg')
        # # Create a raw object, this can be used to create a MNE Epoch object
        # raw = mne.io.RawArray(entry, info)
    else:
        print("Usage: python eeg.py [folder1] [folder2]")
