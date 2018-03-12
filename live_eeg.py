#! /usr/bin/env python3
# Reads live Matlab EEG data
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

import os
import time
import itertools
import numpy as np
import analysis
import classify

LABELS = ['hand-right', 'hand-left', 'foot-right', 'foot-left']


def read_delete_when_available(filename):
    while not os.path.exists(filename):
        time.sleep(50)

    data = np.loadtxt(filename, delimiter=',')
    os.remove(filename)
    return data

def periodically_classify(filename='data.csv'):
    while True:
        data = read_delete_when_available(filename)
        result = analysis.analysis(data[:,0], data[:,1])
        prediction = analysis.KNN.predict([[result[0][0], result[1][0]]])
        print("Classified as {}".format(prediction))

def calibrate(filename):
    calibrate_results = {}
    for label in LABELS:
        calibrate_results[label] = [[], []]
        print('Please think {} for 10 seconds'.format(label))

        for i in range(10):
            data = read_delete_when_available(filename)
            result = analysis.analysis(data[:,0], data[:,1])
            calibrate_results[label][0].append(result[0][0])
            calibrate_results[label][1].append(result[1][0])

    return calibrate_results


def init(filename='data.csv'):
    analysis.KNN = create_knn_classifier(calibrate(filename))

if __name__ == '__main__':
    init()
    print("Calibrating done, classifying each second now...")
    periodically_read()
