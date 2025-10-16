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
        if row["Fertilizer_Used"].strip().lower() == "true":
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

def write_to_csv(avg_yield, fertilised_yield, differences, filename="yield_results.csv"):
    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, filename)

    with open(full_path, mode="w", newline="") as csvfile:
        fieldnames = ["Crop", "Average_Yield_All", "Average_Yield_Fertiliser", "Yield_Difference"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for crop in avg_yield:
            writer.writerow({
                "Crop": crop,
                "Average_Yield_All": round(avg_yield.get(crop, 0), 2),
                "Average_Yield_Fertiliser": round(fertilised_yield.get(crop, 0), 2),
                "Yield_Difference": round(differences.get(crop, 0), 2)
            })

    print(f"Results successfully written to {filename}")

class TestCropFunctions(unittest.TestCase):

    def setUp(self):
        self.data = [
            {"Crop": "Wheat", "Fertilizer_Used": "True", "Yield_tons_per_hectare": "6.0"},
            {"Crop": "Wheat", "Fertilizer_Used": "False", "Yield_tons_per_hectare": "4.0"},
            {"Crop": "Rice", "Fertilizer_Used": "True", "Yield_tons_per_hectare": "7.0"},
            {"Crop": "Rice", "Fertilizer_Used": "False", "Yield_tons_per_hectare": "5.0"},
        ]

    def test_avg_yield_per_crop(self):
        result = avg_yield_per_crop(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertAlmostEqual(result["Wheat"], 5.0)
        self.assertAlmostEqual(result["Rice"], 6.0)

        data_single = [{"Crop": "Corn", "Yield_tons_per_hectare": "10"}]
        result_single = avg_yield_per_crop(data_single)
        self.assertEqual(result_single["Corn"], 10.0)

        result_empty = avg_yield_per_crop([])
        self.assertEqual(result_empty, {})

        with self.assertRaises(ValueError):
            avg_yield_per_crop([{"Crop": "Wheat", "Yield_tons_per_hectare": "abc"}])

    def test_avg_yield_after_fertiliser(self):
        result = avg_yield_after_fertiliser(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertAlmostEqual(result["Wheat"], 6.0)
        self.assertAlmostEqual(result["Rice"], 7.0)

        mixed_data = [
            {"Crop": "Corn", "Fertilizer_Used": "True", "Yield_tons_per_hectare": "8.0"},
            {"Crop": "Corn", "Fertilizer_Used": "False", "Yield_tons_per_hectare": "5.0"},
        ]
        result_mixed = avg_yield_after_fertiliser(mixed_data)
        self.assertAlmostEqual(result_mixed["Corn"], 8.0)

        no_true = [{"Crop": "Wheat", "Fertilizer_Used": "False", "Yield_tons_per_hectare": "4.0"}]
        result_no_true = avg_yield_after_fertiliser(no_true)
        self.assertEqual(result_no_true, {})

        result_empty = avg_yield_after_fertiliser([])
        self.assertEqual(result_empty, {})

    def test_yield_difference(self):
        result = yield_differnce(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertAlmostEqual(result["Wheat"], 1.0)
        self.assertAlmostEqual(result["Rice"], 1.0)

        data_equal = [
            {"Crop": "Corn", "Fertilizer_Used": "True", "Yield_tons_per_hectare": "5.0"},
            {"Crop": "Corn", "Fertilizer_Used": "False", "Yield_tons_per_hectare": "5.0"},
        ]
        result_equal = yield_differnce(data_equal)
        self.assertAlmostEqual(result_equal["Corn"], 0.0)

        data_no_true = [{"Crop": "Corn", "Fertilizer_Used": "False", "Yield_tons_per_hectare": "5.0"}]
        result_no_true = yield_differnce(data_no_true)
        self.assertEqual(result_no_true, {})

        result_empty = yield_differnce([])
        self.assertEqual(result_empty, {})

    def test_write_to_csv(self):
        avg = {"Wheat": 4.5}
        fert = {"Wheat": 5.0}
        diff = {"Wheat": 0.5}
        filename = "test_output.csv"

        write_to_csv(avg, fert, diff, filename)
        self.assertTrue(os.path.exists(filename))

        with open(filename) as f:
            header = f.readline().strip()
        self.assertIn("Crop", header)
        self.assertIn("Average_Yield_All", header)

        filename_empty = "test_empty.csv"
        write_to_csv({}, {}, {}, filename_empty)
        with open(filename_empty) as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)

        for file in [filename, filename_empty]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":

    data = load_data("crop_yield.csv")
    avg = avg_yield_per_crop(data)
    avg_fert = avg_yield_after_fertiliser(data)
    diff = yield_differnce(data)

    unittest.main()
    write_to_csv(avg, avg_fert, diff)


