#! /usr/bin/env python3
# Parses raw eeg session data to easier to use format
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

# TODO: flexible channel selection

import re
import argparse
from scipy.io import loadmat
from scipy.io import savemat
import numpy as np
import os


def parse(filename):
    """ Extract the order of the conditions from the eeg log files. Returns
    a dictionary with the condition name as key and an array of indices as
    value. """
    # The measured conditions. These strings correspond to image filenames in
    # the logfile of the eeg session.
    conditions = {'HandLinks': [], 'HandRechts': [], 'VoetLinks': [],
                  'VoetRechts': [], 'TongOmhoog': []}

    f = open(filename, 'r')
    pattern = r'\b(Image)\b'
    trials = 0
    for line in f:
        # Check if 'Image' is mentioned on the line
        if re.findall(pattern, line):
            # Extract the name of the shown image
            filename = line.split(';')[5]
            # Remove the image extention
            name = filename.split('.')[0]
            if name in conditions:
                conditions[name].append(trials)
                trials += 1

    return conditions, trials


def cut(data, dio):
    """ Cut conditions out of data. """
    low = False
    high = False
    # TODO: explain why startflag and low/high
    start_flag = False
    start = 0
    cnt = 0
    conditions = []
    i = 0

    for line in data:
        # If change from nonzero to zero dio
        if line[dio] == 0 and not low and cnt != 0:
            low = True
            high = False

            if start_flag:
                # Print the length of each trial for debugging purposes
                conditions.append(data[start:cnt])
            i += 1
        # If change from zero to nonzero dio
        elif line[dio] != 0 and not high:
            high = True
            low = False
            start_flag = True
            start = cnt
        cnt += 1

    conditions = np.array(conditions)
    return conditions

# Crop all trials to the same length
def crop(data):
    """ Crop all trials to the same length to create an uniform length data. """
    cnt = 0
    length = min([trial.shape[0] for trial in data])

    for trial in data:
        data[cnt] = trial[:length, :]
        cnt += 1

    return data, length


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


def label_eeg(data, labels, channels):
    """ Label every trial with a condition. """
    out = {}
    for label in labels:
        # Label both recorded channels
        c1 = label_condition(data, labels[label], channels[0])
        c2 = label_condition(data, labels[label], channels[1])
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
    parser = argparse.ArgumentParser(description='Parses results from trials in a easier to use format.')
    parser.add_argument('matlab_file', help='Specify the file in which the recording of the eeg session is stored (.mat)')
    parser.add_argument('log_file', help='Specify the log file of the eeg session recoding (.csv)')
    parser.add_argument('destination_folder', help='Specify the folder in which to store the automatically generated data')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Enable verbose output for debugging purposes')
    parser.add_argument('-i', '--ignore', type=int, default=0, help='The number of trials at the start of the session to ignore. This is to remove rubbish measurements starrt of the session, such as test trials.')
    parser.add_argument('-d', '--dio', type=int, default=-1, help='Specify the channel that contains the dio on the condition, the last channel (-1) by default. The second to last is -2')    
    parser.add_argument('-c', '--channels', nargs=2, type=int, help="Specify the channels", default=[0, 1])

    args = parser.parse_args()
    data_file = args.matlab_file
    log_file = args.log_file
    VERBOSE = args.verbose
    channels = args.channels

    data = loadmat(data_file)['data']
    labels, logfile_trials  = parse(log_file)
    # Cut on the condition; only use the signal when the condition dio was active
    data = cut(data, args.dio)
    # Remove the trials that can be ignored, zero by default
    data = data[args.ignore:]
    # Get the number of trials from the eeg recording
    recording_trials = data.shape[0]

    if VERBOSE:
        print("{} trials were extracted from the eeg logs". format(logfile_trials))
        print("{} trials where extracted from the matlab eeg file".format(recording_trials))

    if recording_trials == 0:
        print("\nERROR: No trials extracted from eeg file. Please check if the correct dio channel is selected.")
        exit(1)

    # Backup the uncropped data
    uncropped_data = np.copy(data)
    # Crop the length of each trial to the same size
    data, trial_length = crop(data)

    if VERBOSE:
        print("Order of the recorded trials:\n{}\n".format(labels))
        print("Length of each trial:")
        i = 0
        for cond in uncropped_data:
            print("Trial {}:\t{}".format(i, cond.shape[0]))
            i += 1
        
        print("Cropping data to {} samples per data".format(trial_length))
    
    # Only continue if the number of trials in the both files are the same
    if recording_trials != logfile_trials:
        msg = ("\nERROR: Number of trials in the log file does not match the "
            "number of trials in the eeg file. Please rerun the program with the "
            "'-v' flag to enable debugging statements. If the number of trials "
            "in the eeg file seems to be one or zero, please check if the dio "
            "channel is correct. This can be changed with the '-d' commandline "
            "option.")
        print(msg)
        exit(1)

    # Match the correct condition label to each trial
    out = label_eeg(data, labels, channels)
    
    if VERBOSE:
        print("SUCCESS: writing data to folder: {}".format(args.destination_folder))
    # Write the generated data to the specified folder
    write_eeg(out, args.destination_folder)
    exit(0)

