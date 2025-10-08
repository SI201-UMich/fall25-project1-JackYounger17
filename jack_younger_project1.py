import csv
import os
import unittest

def load_data(filename):

    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, filename)
    data = []

    with open(full_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            data.append(line)

    return data
