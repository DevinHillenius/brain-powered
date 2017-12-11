#! /usr/bin/env python3

import mne
import sys
from scipy.io import loadmat

def load_eeg_mat(path, label='data'):
    return loadmat(path)[label]

if len(sys.argv) > 1:
    print(load_eeg_mat(sys.argv[1]))
