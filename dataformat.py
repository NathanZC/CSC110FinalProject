"""
test
"""
import csv
from dataclasses import dataclass
from typing import Dict


@dataclass
class Country:
    """A country object containing information processed from the given dataset for each country

Representation Invariants
      - self.name != ''
      - self.code != ''
      - self.population >= 0
      - self.GDP_yearly != {}
      - self.CO2_yearly != {}

Instance Attributes
      - name: the name of the country
      - code: the code assigned to this country
      - population: the population of this country
      - GDP_yearly: a mapping of years to their respective GDP
      - CO2_yearly: a mapping of years to their respective CO2 emission levels
    """
    name: str
    code: str
    population: int
    GDP_yearly: Dict[int, float]
    CO2_yearly: Dict[int, float]


def csv_to_dict(filepath: str) -> Dict[str, Dict[int, float]]:
    """
    Changes the csv file data into a dict of dicts of data where
    the first key is the country that gets mapped to a dict of years to information for that year
    """
    with open(filepath) as file:
        reader = csv.reader(file)
        next(reader)
        data = {row[0]: {} for row in reader}

    with open(filepath) as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if 1990 <= int(row[2]) <= 2017:
                data[row[0]][int(row[2])] = float(row[3])
    return data


filepath = 'gdp-per-capita-worldbank.csv'
with open(filepath) as file:
    reader = csv.reader(file)
    # Skip header row
    next(reader)
    country_codes = {row[0]: row[1] for row in reader}

# Helper dicts
gdp_data = csv_to_dict('gdp-per-capita-worldbank.csv')
co2_data = csv_to_dict('annual-co2-emissions-per-country.csv')
population_data = csv_to_dict('population-by-country.csv')

# Compile all smaller dicts into one mapping of the country to a object with the countries data.
# NOTE: This dict will only contain countries that exist in both the gdp and co2 dataset.
# This is the dataset to be used
all_data = {country_name:
            Country(country_name,
                    country_codes[country_name],
                    int(population_data[country_name][2000]),
                    gdp_data[country_name],
                    co2_data[country_name])
            for country_name in co2_data
            if country_name in gdp_data and country_name in co2_data
            and country_name in population_data and 2000 in population_data[country_name]
            and country_codes[country_name] != ''
            and all(i in gdp_data[country_name] and i in co2_data[country_name] for i in range(1990, 2018))}
