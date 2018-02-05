#! /usr/bin/env python3
# Parses raw trial results in a easier to use format
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

import re
import argparse
from scipy.io import loadmat
from scipy.io import savemat
import numpy as np
import os

VERBOSE = False


def parse(filename):
    """ Extract the order of the conditions from the eeg log files. Returns
    a dictionary with the condition name as key and an array of indices as
    value. """
    conditions = {'HandLinks': [], 'HandRechts': [], 'VoetLinks': [],
                  'VoetRechts': [], 'TongOmhoog': []}

    f = open(filename, 'r')
    pattern = r'\b(Image)\b'
    count = 0
    for line in f:
        # Check if 'Image' is mentioned on the line
        if re.findall(pattern, line):
            # Extract the name of the shown image
            filename = line.split(';')[5]
            # Remove the image extention
            name = filename.split('.')[0]
            if name in conditions:
                conditions[name].append(count)
                count += 1

    if VERBOSE:
        print("Order of the recorded trials:\n{}\n".format(conditions))
        print("{} trials were recorded according to the eeg logs". format(count))
    return conditions


def cut(data):
    """ Cut conditions out of data. """
    low = False
    high = False
    start = 0
    cnt = 0
    conditions = []
    for line in data:
        # If change from nonzero to zero dio
        if line[-1] == 0 and not low and start != 0:
            low = True
            high = False
            
            conditions.append(data[start:cnt])
        # If change from zero to nonzero dio
        elif line[-1] != 0 and not high:
            high = True
            low = False
            start = cnt
        cnt += 1
    
    if VERBOSE:
        trials = np.array(conditions).shape[0]
        print("{} trials where extracted from the matlab eeg file".format(trials))
    return np.array(conditions)

# Crop all trials to the same length
def crop(data):
    """ Crop all trials to the same length to create an uniform length data. """
    cnt = 0
    length = min([trial.shape[0] for trial in data])

    for trial in data:
        data[cnt] = trial[:length, :]
        cnt += 1

    if VERBOSE:
        print("Cropping data to {} samples per data".format(length))
    return data


def get_channel(data, num):
    """ Use a single channel from eeg measurements. """
    return data[:, num]


def label_condition(data, indices, num):
    """ Collect all trials that belong to the same condition. """
    l = []
    for index in indices:
        trial = data[index]
        trial = get_channel(trial, num)
        l.append(trial)
    return np.array(l)


def label_eeg(data, labels):
    """ Label every trial with a condition. """
    out = {}
    for label in labels:
        # Label both recorded channels
        c1 = label_condition(data, labels[label], 0)
        c2 = label_condition(data, labels[label], 1)
        out[label] = (c1, c2)
    return out


def write_eeg(labeled_data, root_folder):
    """ Write the parsed eegfiles to disk """
    for label in labeled_data:
        path = root_folder + '/' + label
        if not os.path.exists(path):
            os.makedirs(path)
        
        savemat(path + '/c1.mat', mdict={'data': labeled_data[label][0]})
        savemat(path + '/c2.mat', mdict={'data': labeled_data[label][1]})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses results from trials \
    in a easier to use format.')
    parser.add_argument('matlab_file', help='Specify the .mat file from the eeg session')
    parser.add_argument('log_file', help='Specify the .csv log file from the eeg session')
    parser.add_argument('destination_folder', help='Specify the folder in which to store the data')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Enable verbose output for debugging purposes')
    args = parser.parse_args()
    data_file = args.matlab_file
    log_file = args.log_file
    VERBOSE = args.verbose
    
    data = loadmat(data_file)['data']
    labels = parse(log_file)

    # Cut sometimes not working (Derk, Lotte)
    data = cut(data)
    data = crop(data)

    out = label_eeg(data, labels)
    if VERBOSE:
        print("Written data to folder: {}".format(args.destination_folder))
    write_eeg(out, args.destination_folder)
