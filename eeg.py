#! /usr/bin/env python3

import mne
import sys
import numpy as np
from scipy.io import loadmat

from sklearn.model_selection import ShuffleSplit


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

def combine_channels(c1, c2):
    """ Combine data from the two channels together in a 3D matrix where
        the shape is (# tests, # channels, # datapoints) """
    return np.concatenate((np.transpose(c1), np.transpose(c2)), axis=1)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        base, cond = load_measurement(sys.argv[1])

        shuffle = ShuffleSplit()
        
        base_labels = np.zeros(base.shape[0])
        cond_labels = np.zeros(cond.shape[0])

        # Input dimensions must be the same
        print(base.shape)
        print(cond.shape)
        train_data = np.concatenate((base, cond))
        
        labels = np.concatenate((base_labels, cond_labels))

        # Assemble a classifier
        lda = LinearDiscriminantAnalysis()
        csp = CSP(n_components=4, reg=None, log=True, norm_trace=False)

        # Use scikit-learn Pipeline with cross_val_score function
        clf = Pipeline([('CSP', csp), ('LDA', lda)])
        scores = cross_val_score(clf, train_data, labels, cv=shuffle, n_jobs=1)

        # Printing the results
        class_balance = np.mean(labels == labels[0])
        class_balance = max(class_balance, 1. - class_balance)
        print("Classification accuracy: %f / Chance level: %f" % (np.mean(scores),
                                                                class_balance))

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
        print("Usage: python eeg.py [path]")
    
