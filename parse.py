import os
import datetime
from collections import defaultdict
import argparse

from timedata import TimeData

DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"


def read_file(file_path):
    """Read the content of the file and return lines."""
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return []
    print(f"Reading from {file_path}")
    with open(file_path, 'r') as file:
        return file.readlines()


def get_timestamp(line):
    """Split the line and return the datetime string"""
    parts = line.strip().split(" ")
    offset = parts[4]
    return f"{parts[2]} {parts[3]} {offset}"


def parse_timestamps(lines):
    """Parse timestamps from the lines of the file."""
    timestamps = set()
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines) and "start time" in lines[i] and "end time" in lines[i + 1]:
            start_time_str = get_timestamp(lines[i])
            end_time_str = get_timestamp(lines[i + 1])
            time_data = TimeData(start_time_string=start_time_str, end_time_string=end_time_str,
                                 date_format=DATE_FORMAT)
            if time_data.delta_minutes is not None:
                timestamps.add(time_data)
    return timestamps


def get_week_end(time_utc):
    """Calculate the end of the week (Sunday) for the given input time."""
    week_end = time_utc + datetime.timedelta(days=(6 - time_utc.weekday()))
    return week_end.replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=datetime.timezone.utc)


def get_current_week_start_and_end():
    """Calculate the start (Monday) and end (Sunday) of the week for the current date and time."""
    current_datetime_utc = datetime.datetime.now(datetime.timezone.utc)
    start_of_week = current_datetime_utc - datetime.timedelta(days=current_datetime_utc.weekday())  # Monday
    return start_of_week, get_week_end(current_datetime_utc)


def group_by_week(time_data_list):
    """Group minutes by their corresponding week ending date and sum them."""
    weekly_minutes = defaultdict(float)

    for time_data in time_data_list:
        week_end = get_week_end(time_data.end_time_utc)
        weekly_minutes[week_end] += time_data.delta_minutes

    return weekly_minutes


def convert_minutes_to_hours(weekly_minutes):
    """Convert minutes to hours for each week."""
    return {week: round(minutes / 60, 2) for week, minutes in weekly_minutes.items()}


def save_results(output_path, time_data_list, weekly_hours):
    """Save the daily minutes and weekly hours to a file."""
    weekly_results = defaultdict(list)

    for time_data in time_data_list:
        week_end = get_week_end(time_data.end_time_utc)
        weekly_results[week_end].append(
            f"Start time: {time_data.start_time_string}, End time: {time_data.end_time_string}, Minutes:{time_data.delta_minutes}\n")

    with open(output_path, 'w') as file:
        for week_end in sorted(weekly_results):
            file.writelines(weekly_results[week_end])
            if week_end in weekly_hours:
                hours = weekly_hours[week_end]
                file.write(f"Week ending {week_end.strftime('%m/%d/%y')}: {hours} hours\n")
                print(f"Week ending {week_end.strftime('%m/%d/%y')}: {hours} hours")
        print(f"Results saved to {output_path}")


def read_existing_entries_as_timedata(output_path):
    """Read existing entries from the file and convert them into a set of TimeData."""
    existing_time_data = set()
    lines = read_file(output_path)
    for line in lines:
        if 'Start time' in line:
            try:
                start_time_string = line.split(', ')[0].split(': ', 1)[1]
                end_time_string = line.split(', ')[1].split(': ', 1)[1]
                existing_time_data.add(TimeData(start_time_string=start_time_string, end_time_string=end_time_string,
                                                date_format=DATE_FORMAT))
            except Exception as e:
                print(f"{e}: Unable to parse {line}")

    return existing_time_data


def output_daily(daily_deltas):
    """Outputs the daily and total time data from a dictionary of daily deltas."""
    # Initialize a total counter for the week
    total_week_minutes = sum(daily_deltas.values())

    print()
    # Print delta times for each day
    for day, delta in sorted(daily_deltas.items()):
        hours = delta / 60  # Convert minutes to hours
        print(f"{day}: {hours:.1f} hours ({round(delta)})")

    # Calculate and print the total for the week
    total_week_hours = total_week_minutes / 60
    print(f"Current week: {total_week_hours:.1f} hours ({round(total_week_minutes)})")


def split_days_by_current_week(sorted_time_data_list):
    """Calculate the start and end of the current week (Monday to Sunday)"""
    start_of_week, end_of_week = get_current_week_start_and_end()

    # Lists to store days in and out of the current week
    days_in_current_week = []
    days_outside_current_week = []

    # Process in reverse order for early stopping
    for time_data in reversed(sorted_time_data_list):
        if time_data.start_time_utc > end_of_week:
            continue  # Skip future entries (if any)

        if time_data.start_time_utc >= start_of_week:
            # Add to the current week list
            days_in_current_week.append(time_data)
        else:
            # Break if we encounter an earlier week since the list is sorted
            days_outside_current_week.append(time_data)
            # break

    return days_in_current_week, days_outside_current_week


def calculate_time_for_each_day_in_current_week(current_week_time_data_list):
    """Calculate the time date for the current week (Monday to Sunday)"""

    # Filter and accumulate delta_minutes for the current week
    daily_deltas = defaultdict(float)  # Default dictionary to accumulate per day

    # Process in reverse order for early stopping
    for time_data in reversed(current_week_time_data_list):
        day = time_data.start_time_utc.date()
        daily_deltas[day] += time_data.delta_minutes

    return daily_deltas


def calculate_weekly_hours(timelog_file_path, output_path):
    """Main function to calculate and output weekly hours from the time log file."""
    existing_time_set = read_existing_entries_as_timedata(output_path)
    timelog_lines = read_file(timelog_file_path)
    time_data_set = parse_timestamps(timelog_lines)
    combined_time_data_set = time_data_set.union(existing_time_set)

    if combined_time_data_set:
        sorted_time_data_list = sorted(list(combined_time_data_set))
        days_in_current_week, days_excluding_current_week = split_days_by_current_week(sorted_time_data_list)

        daily_deltas = calculate_time_for_each_day_in_current_week(days_in_current_week)
        weekly_minutes = group_by_week(days_excluding_current_week)
        weekly_hours = convert_minutes_to_hours(weekly_minutes)
        save_results(output_path, days_excluding_current_week, weekly_hours)
        output_daily(daily_deltas)
    else:
        print(f"There is nothing in {timelog_file_path} that is not already in {output_path}.")


def main():
    parser = argparse.ArgumentParser(description="Process time log file to calculate weekly hours.")
    parser.add_argument('--input', type=str, help='Path to the input time log file',
                        default=os.path.expanduser('~/Documents/timelog.txt'))
    parser.add_argument('--output', type=str, help='Path to the output file', default='./weekly_hours.txt')
    args = parser.parse_args()

    # Calculate weekly hours
    calculate_weekly_hours(args.input, args.output)


if __name__ == '__main__':
    main()
