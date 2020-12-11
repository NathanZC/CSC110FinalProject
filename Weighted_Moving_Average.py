# Michele's stuff for final project:

# Up to now we have a dictionary of the form:
# {'country_str': [{year_int:{GDP_float, CO2_float}]}
# for each of our 30 countries.
# This is a country dictionary: {year_int:{GDP_float, CO2_float}
from typing import Any, List, Dict, Tuple
import math


#################################################################################################################
#######
# Auto-regressive model #  This shit is impossible, just ignore it and go to the WMA lol
#######
#################################################################################################################
def co2_level_yearly_change(country_dictionary: Dict[str, Dict[int, List[float]]]) \
        -> Dict[str, Dict[int, float]]:
    """ Takes a countries CO2 emissions and transforms it into a dict representing the
    change in yearly CO2 emissions of the country. In this case, if we are calculating the
    difference in CO2 levels between 2016 and 2015, then value output representing 2016 would
    be the 2016 emissions minus the 2015 emissions.

    For example:
    Note: in this case, 2015 loses its value, and it doesn't get to participate, as its
    difference cannot be calculated as we do not have a 2014 value.

    >>> country_dict = {'Canada': {2015: [5.346, 1020.50], 2016: [5.350, 1067.50], \
    2017: [5.247, 1004.75]}, 'Panama': {2015: [5.346, 1020.00], 2016: [5.350, 1040.0], \
    2017: [5.247, 1000.0]}}
    >>> result = co2_level_yearly_change(country_dict)
    >>> result == {'Canada': {2016: 47.0, 2017: -62.75}, 'Panama': {2016: 20.0, 2017: -40.0}}
    """

    # ACCUMULATOR: keeps track of our year to CO2 difference dictionary for each country.
    country_to_year_to_co2_so_far = {}

    for country in country_dictionary:

        # ACCUMULATOR: keeps track of our year to CO2 difference dictionary
        year_to_co2_so_far = {}
        years = list(country_dictionary[country].keys())

        for i in range(0, len(years) - 1):
            year_to_co2_so_far[years[i + 1]] = \
                country_dictionary[country][years[i + 1]][1] - country_dictionary[country][years[i]][1]
        country_to_year_to_co2_so_far[country] = year_to_co2_so_far

    return country_to_year_to_co2_so_far


def filter_co2_diff(co2_differences: Dict[str, Dict[int, float]]) -> Dict[str, Dict[int, float]]:
    """ Returns the filtered co2_differences dictionary which removes the years were the
    difference would have negligible effect in our auto-regression (this is a standard
    procedure when using the autoregressive model to predict future data.

    >>> co2_emission_differences = {'Canada': {2016: 7.0, 2017: -2.75}, 'Panama': {2016: 0.4, 2017: 3.2}}
    >>> filter_co2_diff(co2_emission_differences)
    {'Canada': {2016: 7.0, 2017: -2.75}, 'Panama': {2017: 3.2}}
    """

    # the c02 difference from year to year that is negligible
    threshold = 0.5

    # copy of the dict entered by user for mutation to not affect it
    dict_to_filter = co2_differences.copy()

    for country in co2_differences:
        years = list(co2_differences[country].keys())
        for i in range(0, len(years)):
            if abs(co2_differences[country][years[i]]) < threshold:
                dict_to_filter[country].pop(years[i])

    filtered_dict = dict_to_filter
    return filtered_dict

#################################################################################################################
#######
# WMA #
#######
#################################################################################################################

#################################################################################################################
# Calculating the best n to predict future values (period our averages will be based on)
#################################################################################################################

def ma_period(country_dictionary: Dict[str, Dict[int, List[float]]]) -> int:
    """ Figure out the ideal length of the moving average period that will be used
    to predict the future CO2 values of the user-chosen country, by comparing their
    mean value deviation (average error when compared to the CSV actual values).

    >>> country_dict = {'Canada': {2015: [5.346, 1020.50], 2016: [5.350, 1067.50], \
    2017: [5.247, 1004.75], 2018: [5.346, 1020.00], 2019: [5.350, 1040.0], \
    2020: [5.247, 1018.0]}}
    >>> result = ma_period(country_dict)
    >>> result == 3
    """

    country = list(country_dictionary.keys())[0]
    time_period = country_dictionary[country]

    possible_n = [n for n in range(0, len(time_period)) if 1 < n < len(time_period)]

    # Transform dict into list of tuples.
    years_to_values = list(country_dictionary[country].keys())
    value_list = [(year, country_dictionary[country][year][1]) for year in years_to_values]

    # ACCUMULATOR: keeps track of our current moving_average and possible_n. It is a dict
    # with key possible_n and corresponding value list
    n_to_moving_average = {}

    # Generate a dict mapping n to its moving averages
    for n in possible_n:
        n_to_moving_average[n] = w_average_n_values(n, value_list)

    # ACCUMULATOR: keeps track of the tuple of mad values to their corresponding n.
    mad_n_so_far = []

    # Generate mad to n tuples
    for n_value in n_to_moving_average:
        mad_n_so_far.append(mean_absolute_deviation(n_value, value_list, n_to_moving_average[n_value]))

    possible_n_values = [item[0] for item in mad_n_so_far]
    lowest_error_average = min(possible_n_values)
    final_n = [item[1] for item in mad_n_so_far if item[0] == lowest_error_average]

    return final_n[0]


def w_average_n_values(n: int, value_list: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """ Return averages of years based on the value n and the following weight distribution:
    - most recent item * 0.n
    - second most recent item * 0.n-1
    - and so on until 0.1.

    Preconditions:
        - 1 < n <= 9

    As pointed in at in the preconditions, n has to be higher than 1, so that we are not just simply
    calculating the slope, and less than or equal to n, as that is the point where we have decided
    data is no longer too impactful.

    >>> year_to_co2 = [(2010, 170), (2011, 184.2), (2012, 192.1), (2013, 185.7),\
    (2014, 201.4), (2015, 195), (2016, 202.3), (2017, 208.7)]
    >>> w_average_n_values(3, year_to_co2)
    [(2013, 185.8), (2014, 187.5), (2015, 194.6), (2016, 195.6),\
    (2017, 199.7)]
    """

    # ACCUMULATOR: keeps track of of the year and moving averages according to n.
    year_to_ma_co2_so_far = []  # list of tuples

    for i in range(0, len(value_list) - n):
        current_years = value_list[i: i + n]
        current_co2_values = [value[1] for value in current_years]

        # ACCUMULATOR: keeps track of the current weighted co2 values.
        current_weighted_co2_values = []

        user_n = 0.1  # weight for the least impactful value
        j = 0  # iteration variable
        total_weight = 0  # keeps track of the total weight of a period.

        while (user_n * 10) < n + 1:
            current_weighted_co2_values.append(current_co2_values[j] * user_n)
            total_weight = total_weight + user_n
            user_n = user_n + 0.1
            j = j + 1

        year_to_ma_co2_so_far.append((value_list[i][0] + n, sum(current_weighted_co2_values) / total_weight))

    return year_to_ma_co2_so_far


def mean_absolute_deviation(n: int, value_list: List[Tuple[int, float]],
                            ma_values: List[Tuple[int, float]]) -> Tuple[float, int]:
    """ Return the mean absolute deviation. That is, the average of the differences between
    the ma_values that result from calling average_n_values on n and value_list (referring
    to CO2 emissions) and the values from the country_dictionary. This
    is used to decide which n value more appropriate in the function ma_period, as the smaller the error average, the
    better the n value is to predict the future values.

    Preconditions:
        - len(value_list) == len(ma_values) + n

    >>> year_to_co2 = [(2010, 170), (2011, 184.2), (2012, 192.1), (2013, 185.7),\
    (2014, 201.4), (2015, 195), (2016, 202.3), (2017, 208.7)]
    >>> ma_co2_values = [(2013, 185.8), (2014, 187.5), (2015, 194.6), (2016, 195.6),\
    (2017, 199.7)]
    >>> result = mean_absolute_deviation(3, year_to_co2, ma_co2_values)
    >>> math.isclose(result[0], 6.02)
    True
    """
    # ACCUMULATOR: keeps track of the differences between the value_list and ma_values values (errors of forecast).
    differences_so_far = []

    for i in range(0, len(ma_values)):
        differences_so_far.append(abs(value_list[i + n][1] - ma_values[i][1]))

    mad = sum(differences_so_far) / len(ma_values)  # mad: Mean Absolute Deviation

    return (mad, n)


#################################################################################################################
# Applying the Weighted Moving Average to predict future values
#################################################################################################################
def wma_prediction(n: int, x: int, country_dictionary: Dict[str, Dict[int, List[float]]]) -> List[Tuple[int, float]]:
    """ Return the prediction for the following x years based on the n provided in the form of
    a list of floats.

    Preconditions:
        - x < n

    >>> country_dict = {'Canada': {2010: [5.346, 170], 2011: [5.350, 184.2], \
    2012: [5.247, 192.1], 2013: [5.346, 185.7], 2014: [5.350, 201.4], \
    2015: [5.247, 195], 2016:[4.365, 202.3], 2017:[4.68, 208.7]}}
    >>> wma_prediction(3, 2, country_dict)
    [(2018, 204.3), (2019, 205.4)]
    """

    country = list(country_dictionary.keys())[0]

    years = list(country_dictionary[country].keys())
    value_list = [(year, country_dictionary[country][year][1]) for year in years]

    # Slice value list such that only the needed values are present.
    new_value_list = value_list[-n: len(value_list)]

    # ACCUMULATOR: keeps track of of the year and moving averages according to n.
    year_to_ma_co2_so_far = value_list.copy()  # list of tuples

    i = 0  # iteration variable

    while len(year_to_ma_co2_so_far) <= len(value_list) + x:


        # ACCUMULATOR: keeps track of the current weighted co2 values.
        current_weighted_co2_values = []

        user_n = 0.1  # weight for the least impactful value
        j = 0  # iteration variable
        total_weight = 0  # keeps track of the total weight of a period.

        while (user_n * 10) < n + 1:
            current_weighted_co2_values.append(new_value_list[j][1] * user_n)
            total_weight = total_weight + user_n
            user_n = user_n + 0.1
            j = j + 1

        current_weighted_average = sum(current_weighted_co2_values) / total_weight
        year_to_ma_co2_so_far.append((new_value_list[-1][0] + 1, current_weighted_average))
        new_value_list.append((new_value_list[-1][0] + 1, current_weighted_average))
        i = i + 1

        # Slice value list such that only the needed values are present.
        new_value_list = new_value_list[-n: len(new_value_list)]

    return year_to_ma_co2_so_far
