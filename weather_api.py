from datetime import date, timedelta

import datetime
import random
from flask import app

def generate_temperature(hour, month):
    temp_intervals = [(-3.8, 7.7),
                      (-2.7, 10),
                      (-1.1, 14.4),
                      (1.6, 17.7),
                      (5, 22.7),
                      (8.3, 27.8),
                      (11.6, 33.3),
                      (10.5, 32.8),
                      (7.2, 28.3),
                      (2.2, 21.1),
                      (-1.6, 11.6),
                      (-3.8, 7.2)]

    low, high = temp_intervals[month]
    interval = high - low

    if 6 >= hour < 12:
        return random.uniform(low + (interval / 3), high - (interval / 3))
    elif 12 >= hour < 18:
        return random.uniform(low + (interval / 3), high + (interval / 3))
    elif 18 >= hour < 24:
        return random.uniform(low + (interval / 3), high)
    else:
        return random.uniform(low, low + (interval / 3))


def generate_historical_data():
    starting_year = 2022
    starting_month = 1
    starting_day = 1

    minute_increment = timedelta(minutes=15)
    stream_stop = False

    while
