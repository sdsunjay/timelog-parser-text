
# Timelog Parser for Text Files
Log timestamps and calculates weekly work hours.

## Overview
This script is designed to parse time-related data from a file, calculate the total minutes for each time interval, and then group these intervals by the week they fall into. The results are saved in a specified output file, with existing entries being merged with new ones.

## Requirements
- Python 3.x
- `timedata` module (assuming it's defined in `timedata.py` in the same directory)

## File Contents
### Important Functions
- `get_timestamp(line)`: Extracts and returns the timestamp from a line.
- `parse_timestamps(lines)`: Parses timestamps from the lines of the file.
- `group_by_week(time_data_list)`: Groups the minutes by the week they belong to and sums them.
- `save_results(output_path, time_data_list, weekly_hours)`: Saves the results to the specified output file.
- `read_existing_entries_as_timedata(output_path)`: Reads existing entries from the file and converts them into a set of TimeData.
- `calculate_weekly_hours(timelog_file_path, output_path)`: Main function to calculate weekly hours from the time log file.

## Usage
1. Ensure you have the `timedata` module in the same directory.
2. Place your input file (`timelog.txt`) in the `~/Documents` directory, or specify the path using the `--input` argument.
3. Run the script:
    ```bash
    python parse.py [--input <input_file_path>] [--output <output_file_path>]
    ```

If no input file is specified, the script will default to `~/Documents/timelog.txt`. If no output file is specified, the results will be saved to `./weekly_hours.txt`.

### Example
To use the script with default paths:
```bash
python parse.py
```

To specify the input and output files:
```bash
python parse.py --input /path/to/timelog.txt --output /path/to/weekly_hours.txt
```

### Sample Input File
Here is an example of what the input file might look like:
```
start time 2024-06-10 15:15:17 -0400
end time 2024-06-11 01:01:35 -0400
start time 2024-06-11 03:13:35 -0400
end time 2024-06-11 04:10:35 -0400
start time 2024-06-12 21:58:14 -0400 - some commment
end time 2024-06-13 02:11:22 -0400
start time 2024-06-14 03:00:54 -0400
end time 2024-06-14 07:45:27 -0400
start time 2024-06-14 03:00:54 -0400
```
```

## Notes
- Ensure the date format in your input file matches the expected format in the script: `%Y-%m-%d %H:%M:%S %z`.
- The script will print an error if the file does not exist or if there are issues with date parsing.
- The script will print an error if the "end time" is before the "start time"
- The results will exclude the current week's data.

## Output
The results will be saved to the user specified output file or `weekly_hours.txt` in the current directory, with each week's total hours listed.

