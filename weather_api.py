from datetime import date, timedelta

import datetime
import random
from flask import app
import csv

def generate_weather_data(hour, month):
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
                      (-3.8, 7.2),
                      (-4.8, 5.2)]

    rainfall_avg = [3.18, 2.16, 1.69, 1.02, 1.02, 0.81, 0.43, 0.43, 0.55, 1.25, 2.48, 3.5, 3.3]

    low, high = temp_intervals[month]
    interval = high - low

    if 6 >= hour < 12:
        temp = random.uniform(low + (interval / 3), high - (interval / 3))
    elif 12 >= hour < 18:
        temp = random.uniform(high - (interval / 3), high)
    elif 18 >= hour < 24:
        temp = random.uniform(low + (interval / 3), high - (interval / 3))
    else:
        temp = random.uniform(low, low + (interval / 3))

    rainfall_avg_value = rainfall_avg[month]
    rainfall = random.uniform(rainfall_avg_value * 0.5, rainfall_avg_value * 1.5)

    return round(temp, 1), round(rainfall, 1)



def generate_historical_data(file_name):
    final_json = {'results': []}
    starting_year, starting_month, starting_day = 2022, 1, 1
    starting_hour, starting_minute, starting_second, starting_micro = 0, 0, 0, 0

    minute_increment = timedelta(minutes=15)

    current_time = datetime.datetime(year=starting_year,
                                     month=starting_month,
                                     day=starting_day,
                                     hour=starting_hour,
                                     minute=starting_minute,
                                     second=starting_second,
                                     microsecond=starting_micro,
                                     tzinfo=datetime.timezone(datetime.timedelta(hours=-8)))

    while current_time < datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-8))):
        time_string = current_time.isoformat(timespec='milliseconds')
        temp, rainfall = generate_weather_data(current_time.hour, current_time.month)
        current_time += minute_increment

        final_json['results'].append({'time': time_string, 'temp': temp, 'rainfall': rainfall})

    with open(file_name, "w") as final_f:
        final_f.write(str(final_json))


if __name__ == "__main__":
    generate_historical_data('test.txt')