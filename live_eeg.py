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

#LABELS = ['hand-right', 'hand-left', 'foot-right', 'foot-left']
LABELS = sorted(['hand-right', 'hand-left', 'foot'])
calibrations_folder = 'calibrations'


MAPPING = {'hand-right': 'rotate_right',
           'hand-left': 'rotate_left',
           'foot': 'forward'}

NUM_PLOT_CLASSIFICATION = 3

DRONE = drone.Drone()

def read_delete_when_available(filename):
    while not os.path.exists(filename):
        time.sleep(0.05)
    time.sleep(0.1)
    data = np.loadtxt(filename, delimiter=',')
    #print("Measuring...")
    while True:
        try:
            os.remove(filename)
            break
        except:
            continue
    return data

def periodically_classify(calibration, filename='data.csv', drone=None):
    while True:
        data = read_delete_when_available(filename)
        result = analysis.analysis([data[:,0]], [data[:,1]])
        calibration['new'] = [[result[0][0]], [result[1][0]]]
        prediction = analysis.KNN.predict_proba([[result[0][0], result[1][0]]])
        label_classification(calibration, prediction, drone)

def label_classification(calibration, prediction, drone):
    max_prediction = max(prediction[0])
    label = np.argmax(prediction[0])

    print(prediction[0])
    if max_prediction >= 0.8:
        print("Predicted {} at {} confidence".format(LABELS[label], max_prediction))

        if drone != None:
            print("Moving drone!")
            DRONE.move(MAPPING[LABELS[label]], 1)
        if NUM_PLOT_CLASSIFICATION > 0:
            NUM_PLOT_CLASSIFICATION -= 1
            show_calibration(calibration)
        else:
            time.sleep(3)
        return True
    else:
        print("No classification")

    return False

def calibrate(filename, measurements=20, sep=1):
    calibrate_results = {}
    for label in LABELS:
        calibrate_results[label] = [[], []]

    for j in range(sep):
        for label in LABELS:
            print('Please think {} for {} seconds'.format(label, measurements))
            time.sleep(3)

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
    analysis.KNN = classify.create_knn_classifier(calibration, LABELS)
    return calibration

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Live eeg classification demonstration')
    parser.add_argument('subject_name', help='The name of the measured subject.')
    parser.add_argument('-c', '--calibration_file',default=None, help='Load a calibration.')
    args = parser.parse_args()

    #drone = init(args)
    calibration = init(args)
    print("Classifying each second")
    #periodically_classify(drone)
    DRONE.takeoff()
    periodically_classify(calibration)
