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

def avg_yield_per_crop(data):

    crop_yield = {}
    for row in data:
        crop = row["Crop"]
        yield_per_hectare = float(row["Yield_tons_per_hectare"])

        if crop not in crop_yield:
            crop_yield[crop] = []
        crop_yield[crop].append(yield_per_hectare)

    avg_yield = {}
    for crop, values in crop_yield.items():
        total = sum(values)
        count = len(values)
        avg_yield[crop] = total / count

    return avg_yield

def avg_yield_after_fertiliser(data):

    fertilised_rows = []
    for row in data:
        if row["Fertiliser_used"].lower() == "yes":
            fertilised_rows.append(row)

    return avg_yield_per_crop(fertilised_rows)

def yield_differnce(data):

    normal_crop = avg_yield_per_crop(data)
    fertilisised_crop = avg_yield_after_fertiliser(data)

    difference = {}

    for crop in fertilisised_crop:
        diff = fertilisised_crop[crop] - normal_crop[crop]
        difference[crop] = diff

    return difference