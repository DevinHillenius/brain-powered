#! /usr/bin/env python3

import mne
import sys
import numpy as np
from scipy.io import loadmat


def load_eeg_mat(path, label='data'):
    return loadmat(path)[label]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = load_eeg_mat(sys.argv[1])
        # A single response in a trial
        entry = np.transpose(data[:, :, 0])

        # Not sure if we actually need this, we should be able to use the sklearn
        # libraries with just the numpy matrices without the need to use MNE

        # The second argument, sample frequency, is not the real sample frequency
        info = mne.create_info(["Channel 1"], 10, 'eeg')
        # Create a raw object, this can be used to create a MNE Epoch object
        raw = mne.io.RawArray(entry, info)
    else:
        print("Usage: python eeg.py [eeg file path]")

