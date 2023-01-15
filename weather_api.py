from datetime import date, timedelta

from numpy.random import choice
import datetime
import random
import csv

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


def generate_weather_data(hour, month):
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

    minute_increment = timedelta(seconds=5)

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


def generate_fake_stream(file_name, start_year=2023, start_month=1, start_day=16,
                         start_hour=8, start_minute=30, start_second=0,
                         duration_days=1):
    current_time = datetime.datetime(year=start_year,
                                     month=start_month,
                                     day=start_day,
                                     hour=start_hour,
                                     minute=start_minute,
                                     second=start_second,
                                     tzinfo=datetime.timezone(datetime.timedelta(hours=-8)))
    target_time = current_time + timedelta(days=duration_days)
    iteration = timedelta(seconds=5)

    temp_lo, temp_hi = temp_intervals[start_month]
    avg_rainfall = rainfall_avg[start_month]

    # 50% prob of raining
    if random.random() <= 0.5:
        current_temp = round(random.uniform(temp_lo, temp_lo + 5), 1)
        current_rainfall = round(random.uniform(avg_rainfall - 0.2, avg_rainfall + 0.2), 1)
        current_streamflow = 170
        transition_probabilities = {'temp': [0.4, 0.4, 0.2], 'rainfall': [0.2, 0.4, 0.4], 'streamflow': [0.1, 0.2, 0.7]}
    else:
        current_temp = round(random.uniform(temp_lo, temp_hi), 1)
        current_rainfall = 0
        current_streamflow = 200
        transition_probabilities = {'temp': [0.2, 0.4, 0.4], 'rainfall': [0.1, 0.6, 0.3], 'streamflow': [0.3, 0.6, 0.1]}

    with open(file_name, mode="w", newline="") as csv_f:
        writer = csv.writer(csv_f, delimiter=",")
        writer.writerow(["time", "temp", "rain", "streamflow"])
        while current_time < target_time:
            timestamp_str = current_time.isoformat(timespec='milliseconds')

            writer.writerow([timestamp_str, current_temp, current_rainfall, current_streamflow])

            decisions = ['less', 'same', 'more']
            temp_decision = choice(decisions, 1, p=transition_probabilities.get('temp'))
            rain_decision = choice(decisions, 1, p=transition_probabilities.get('rainfall'))
            flow_decision = choice(decisions, 1, p=transition_probabilities.get('streamflow'))

            current_temp = (current_temp - 0.1) if temp_decision == 'less' \
                            else current_temp if temp_decision == 'same' \
                            else (current_temp + 0.1)
            current_temp = round(current_temp, 1)
            current_rainfall = (current_rainfall - 0.1) if rain_decision == 'less' \
                                else current_rainfall if rain_decision == 'same' \
                                else (current_rainfall + 0.1)
            current_rainfall = round(max(current_rainfall, 0), 1)
            current_streamflow = (current_streamflow - 0.1) if flow_decision == 'less' \
                                 else current_streamflow if flow_decision == 'same' \
                                 else (current_streamflow + 0.1)
            current_streamflow = round(max(current_streamflow, 0), 1)

            current_time += iteration


if __name__ == "__main__":
    # generate_historical_data('test.txt')
    generate_fake_stream("test_stream.csv")