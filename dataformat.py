"""
test
"""
import csv
filepath = 'gdp-per-capita-worldbank.csv'
filepath2 = 'annual-co2-emissions-per-country.csv'


def csv_to_dict(filepath) -> dict:
    """
    Changes the csv file data into a dict of dicts of data
    """
    with open(filepath) as file:
        reader = csv.reader(file)

        # Skip header row
        next(reader)
        data = {row[0]: {} for row in reader}

    with open(filepath) as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            data[row[0]][row[2]] = row[3]
    return data


# The two dicts to be used
gdp_data = csv_to_dict('gdp-per-capita-worldbank.csv')
co2_data = csv_to_dict('annual-co2-emissions-per-country.csv')
