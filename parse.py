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
        if i + 1 < len(lines) and "start time" in lines[i] and "end time" in lines[i+1]:
            start_time_str = get_timestamp(lines[i])
            end_time_str = get_timestamp(lines[i+1])
            time_data = TimeData(start_time_string=start_time_str, end_time_string=end_time_str, date_format=DATE_FORMAT)
            if time_data.delta_minutes is not None:
                timestamps.add(time_data)
    return timestamps

def group_by_week(time_data_list):
    """Group the minutes by the week they belong to and sum them."""
    weekly_minutes = defaultdict(float)
    cur_week_end = current_week_end()

    for time_data in time_data_list:
        week_end = get_week_end(time_data.end_time_utc)
        weekly_minutes[week_end] += time_data.delta_minutes

    # Remove the last week for the weekly hours
    weekly_minutes.pop(cur_week_end, None)
    return weekly_minutes

def get_week_end(time_utc):
    """Calculate the end of the week (Sunday) for the given input time."""
    week_end = time_utc + datetime.timedelta(days=(6 - time_utc.weekday()))
    return week_end.replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=datetime.timezone.utc)

def current_week_end():
    """Calculate the end of the week (Sunday) for the current time."""
    current_time_utc = datetime.datetime.now(datetime.timezone.utc)
    return get_week_end(current_time_utc)

def convert_minutes_to_hours(weekly_minutes):
    """Convert minutes to hours for each week."""
    return {week: round(minutes / 60, 2) for week, minutes in weekly_minutes.items()}

def save_results(output_path, time_data_list, weekly_hours):
    """Save the daily minutes and weekly hours to a file."""
    weekly_results = defaultdict(list)

    for time_data in time_data_list:
        week_end = get_week_end(time_data.end_time_utc)
        weekly_results[week_end].append(f"Start time: {time_data.start_time_string}, End time: {time_data.end_time_string}, Minutes:{time_data.delta_minutes}\n")

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
                existing_time_data.add(TimeData(start_time_string=start_time_string, end_time_string=end_time_string, date_format=DATE_FORMAT))
            except Exception as e:
                print(f"{e}: Unable to parse {line}")

    return existing_time_data

def calculate_weekly_hours(timelog_file_path, output_path):
    """Main function to calculate weekly hours from the time log file."""
    existing_time_set = read_existing_entries_as_timedata(output_path)
    timelog_lines = read_file(timelog_file_path)
    time_data_set = parse_timestamps(timelog_lines)
    combined_time_data_set = time_data_set.union(existing_time_set)
    combined_time_data_list = sorted(list(combined_time_data_set))

    if combined_time_data_set:
        weekly_minutes = group_by_week(combined_time_data_list)
        weekly_hours = convert_minutes_to_hours(weekly_minutes)
        save_results(output_path, combined_time_data_list, weekly_hours)
    else:
        print(f"There is nothing in {timelog_file_path} that is not already in {output_path}.")



def main():
    parser = argparse.ArgumentParser(description="Process time log file to calculate weekly hours.")
    parser.add_argument('--input', type=str, help='Path to the input time log file', default=os.path.expanduser('~/Documents/timelog.txt'))
    parser.add_argument('--output', type=str, help='Path to the output file', default='./weekly_hours.txt')
    args = parser.parse_args()

    # Calculate weekly hours
    calculate_weekly_hours(args.input, args.output)

if __name__ == '__main__':
    main()
