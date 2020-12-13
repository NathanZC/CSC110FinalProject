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
      - self.gdp_yearly != {}
      - self.co2_yearly != {}

Instance Attributes
      - name: the name of the country
      - code: the code assigned to this country
      - population: the population of this country
      - gdp_yearly: a mapping of years to their respective GDP
      - co2_yearly: a mapping of years to their respective CO2 emission levels
    """
    name: str
    code: str
    population: int
    gdp_yearly: Dict[int, float]
    co2_yearly: Dict[int, float]


def csv_to_dict(filepath: str) -> Dict[str, Dict[int, float]]:
    """
    Changes the csv file data into a dict of dicts of data where
    the first key is the country that gets mapped to a dict of years to information for that year
    """
    with open(filepath) as file:
        read = csv.reader(file)
        next(read)
        info = {}
        for row in read:
            info[row[0]] = {}

    with open(filepath) as file:
        read = csv.reader(file)
        next(read)
        for row in read:
            if 1990 <= int(row[2]) <= 2017:
                info[row[0]][int(row[2])] = float(row[3])
    return info


def codes_to_dict(filepath: str) -> Dict[str, str]:
    """
    Changes the csv file data into a dict of dicts of data where
    the countries are mapped the their corresponding codes
    """
    with open(filepath) as f:
        reader = csv.reader(f)
        # Skip header row
        next(reader)
        country_codes = {row[0]: row[1] for row in reader}
    return country_codes


def get_all_data() -> Dict[str, Country]:
    """
    returns a dict with all of the data.
    Compiles all smaller dicts into one mapping of the country to a object with the countries data.
    >>> result = get_all_data()
    >>> result['Canada'].gdp_yearly[2000]
    37431.9169780243
    >>> result['Canada'].code == 'CAN'
    True
    >>> result['Canada'].name == 'Canada'
    True
    >>> result['Canada'].co2_yearly[2000] == 571.5073457
    True
    """
    # Helper dicts
    gdp_data = csv_to_dict('gdp-per-capita-worldbank.csv')
    co2_data = csv_to_dict('annual-co2-emissions-per-country.csv')
    population_data = csv_to_dict('population-by-country.csv')
    country_codes = codes_to_dict('gdp-per-capita-worldbank.csv')
    # main dict created using helpers
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
                and all(i in gdp_data[country_name] and i in co2_data[country_name]
                        for i in range(1990, 2018))}
    return all_data


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'extra-imports': ['python_ta.contracts', 'dataclasses', 'datetime', 'csv'],
        'allowed-io': ['csv_to_dict', 'codes_to_dict']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = False
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
