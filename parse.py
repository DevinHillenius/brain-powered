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


def parse(filename):
    conditions = {'HandLinks': [], 'HandRechts': [], 'VoetLinks': [],
                  'VoetRechts': [], 'TongOmhoog': []}

    f = open(filename, 'r')
    pattern = r'\b(Image)\b'
    count = 0
    for line in f:
        if re.findall(pattern, line):
            # Extract the name of the shown image
            filename = line.split(';')[5]
            # Remove the image extention
            name = filename.split('.')[0]
            if name in conditions:
                conditions[name].append(count)
                #print('Trial {}, {}'.format(count, name))
                count += 1

    # Uncomment to print the conditions with indices
    #for condition in conditions: 
    #    print("{}: {}".format(condition, conditions[condition]))
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
    return np.array(conditions)

# TODO: not sure what to do with this
def crop(data):
    cnt = 0
    for trial in data:
        #print(trial.shape)
        data[cnt] = trial[:1281, :]
        #print(data[cnt].shape)
        cnt += 1
    return data


def get_channel(data, num):
    return data[:, num]


def label_condition(data, indices, num):
    """ Match the conditions with the correct labels """
    l = []
    for index in indices:
        trial = data[index]
        trial = get_channel(trial, num)
        l.append(trial)
    return np.array(l)


def label_eeg(data, labels):
    """ Use the labels from the eeg log to label the eeg data """
    out = {}
    for label in labels:
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
    parser.add_argument('filename', nargs=2, help='Select .mat and accompanying csv file')
    args = parser.parse_args()
    data_file = args.filename[0]
    log_file = args.filename[1]

    # OVerwrite temporarily
    #data_file = 'data/BP_Ron.mat'
    #log_file = 'data/results_ron.csv'

    data = loadmat(data_file)['data'] 
    labels = parse(log_file)
    #print(labels)

    data = cut(data)
    #print(labels)
    i = 0
    for trial in data:
        #if trial.shape[0] < 2000:
        i += 1
        print(trial.shape)
    #print(i)
    data = crop(data)
    #print(data[0].shape)
    out = label_eeg(data, labels)
    write_eeg(out, 'test')