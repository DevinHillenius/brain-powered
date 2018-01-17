#! /usr/bin/env python3
# Parses raw trial results in a easier to use format
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

import re
import argparse


def parse(filename):
    conditions = {'HandLinks': [], 'HandRechts': [], 'VoetLinks': [],
                  'VoetRechts': [], 'TongOmhoog': []}

    f = open('data/results_blom.csv', 'r')
    pattern = r'\b(Image)\b'
    count = 1
    for line in f:
        if re.findall(pattern, line):
            # Extract the name of the shown image
            filename = line.split(';')[5]
            # Remove the image extention
            name = filename.split('.')[0]
            if name in conditions:
                conditions[name].append(count)
                print('Trial {}, {}'.format(count, name))
                count += 1

    for condition in conditions:
        print("{}: {}".format(condition, conditions[condition]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses results from trials \
    in a easier to use format.')
    parser.add_argument('filename', help='Select csv file to use')
    args = parser.parse_args()
    parse(args.filename)
