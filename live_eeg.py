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
import pickle
import argparse
import drone

LABELS = ['hand-right', 'hand-left', 'foot-right', 'foot-left']
calibrations_folder = 'calibrations'


MAPPING = {'hand-right': 'forward',
           'hand-left': 'backward',
           'foot-right': 'rotate',
           'foot-left': 'rotate'}

def read_delete_when_available(filename):
    while not os.path.exists(filename):
        time.sleep(0.05)
    time.sleep(0.1)
    data = np.loadtxt(filename, delimiter=',')
    print("Measuring...")
    while True:
        try:
            os.remove(filename)
            break
        except:
            continue
    return data

def periodically_classify(filename='data.csv', drone=None):
    while True:
        data = read_delete_when_available(filename)
        result = analysis.analysis([data[:,0]], [data[:,1]])
        prediction = analysis.KNN.predict_proba([[result[0][0], result[1][0]]])
        label_classification(prediction, drone)

def label_classification(prediction, drone):
    max_prediction = max(prediction[0])
    label = np.argmax(prediction)

    print(prediction[0])
    if max_prediction >= 0.5:
        print("Predicted {} at {} confidence".format(LABELS[label], max_prediction))
        if drone != None:
            print("Moving drone!")
            drone.move(MAPPING[LABELS[label]], 1)
    else:
        print("No classification")
        
def calibrate(filename, measurements=5):
    calibrate_results = {}
    for label in LABELS:
        calibrate_results[label] = [[], []]
        print('Please think {} for {} seconds'.format(label, measurements))

        for i in range(measurements):
            data = read_delete_when_available(filename)
            c1 = data[:, 0]
            c2 = data[:, 1]
            result = analysis.analysis([c1], [c2])
            calibrate_results[label][0].append(result[0][0])
            calibrate_results[label][1].append(result[1][0])

    return calibrate_results

def show_calibration(calibration):
    analysis.plot(calibration)

def save_calibration(calibration, filename):
    with open(filename, 'wb') as file:
        pickle.dump(calibration, file)

def load_calibration(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)
    
def init(args, filename='data.csv'):
    if args.calibration_file:
        calibration = load_calibration(args.calibration_file)
        print("Sucessfully loaded {}".format(args.calibration_file))
    else:
        calibration = calibrate(filename)
        print("Calibration done")
        path = os.path.join(calibrations_folder, args.subject_name + '.augurkje')
        print('Saving calibration to {}'.format(path))
        save_calibration(calibration, path)
    show_calibration(calibration)
    analysis.KNN = classify.create_knn_classifier(calibration)
    return Drone()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Live eeg classification demonstration')
    parser.add_argument('subject_name', help='The name of the measured subject.')
    parser.add_argument('-c', '--calibration_file',default=None, help='Load a calibration.')
    args = parser.parse_args()
     
    drone = init(args)
    print("Classifying each second")
    periodically_classify(drone)
