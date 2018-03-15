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

LABELS = ['hand-right', 'hand-left', 'foot-right', 'foot-left']


def read_delete_when_available(filename):
    while not os.path.exists(filename):
        #print("waiting for 50 ms");
        time.sleep(0.05)
    #print("Reading data")
    time.sleep(0.1)
    data = np.loadtxt(filename, delimiter=',')
    print("Measuring...")
    while True:
        try:
            #print("trying to remove")
            os.remove(filename)
            break
        except:
            continue
    return data

def periodically_classify(filename='data.csv'):
    while True:
        data = read_delete_when_available(filename)
        result = analysis.analysis([data[:,0]], [data[:,1]])
        prediction = analysis.KNN.predict_proba([[result[0][0], result[1][0]]])
        #print("Classified as {}".format(prediction))
        label_classification(prediction)

def label_classification(prediction):
    max_prediction = max(prediction[0])
    label = np.argmax(prediction)
    
    print(prediction[0])
    if max_prediction >= 0.5:
        print("Predicted {} at {} confidence".format(LABELS[label], max_prediction))
    else:
        print("No classification")
        
def calibrate(filename):
    calibrate_results = {}
    for label in LABELS:
        calibrate_results[label] = [[], []]
        print('Please think {} for 10 seconds'.format(label))

        for i in range(5):
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
    
def init(filename='data.csv'):
    calibration = calibrate(filename)
    analysis.KNN = classify.create_knn_classifier(calibration)
    save_calibration(calibration, 'augurkje')
    

if __name__ == '__main__':
    init()
	#while True:
	#	read_delete_when_available('data.csv')
    #calibration = calibrate('data.csv')
    #save_calibration(calibration, 'augurkje')
    #calibration = load_calibration('augurkje')
    print("Calibrating done, classifying each second now...")
    #show_calibration(calibration)
    periodically_classify()
