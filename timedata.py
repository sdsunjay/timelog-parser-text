from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class TimeData:
    start_time_string: str
    end_time_string: str
    start_time_utc: datetime = field(init=False)
    end_time_utc: datetime = field(init=False)
    delta_minutes: float = field(init=False)

    def __post_init__(self):
        # Parse the date strings into datetime objects with timezone info
        start_time = datetime.strptime(self.start_time_string, "%Y-%m-%d %H:%M:%S %z")
        end_time = datetime.strptime(self.end_time_string, "%Y-%m-%d %H:%M:%S %z")

        # Convert both datetime objects to UTC for accurate delta calculation
        self.start_time_utc = start_time.astimezone(timezone.utc)
        self.end_time_utc = end_time.astimezone(timezone.utc)
        if self.end_time_utc < self.start_time_utc:
            # Log an error message and set delta_minutes to None
            print(f"Error:{self.end_time_string} ({self.end_time_utc}) is earlier than {self.start_time_string} ({self.start_time_utc}).")
            self.delta_minutes = None

        else:
            # Calculate the delta between the two times
            delta = self.end_time_utc - self.start_time_utc

            # Convert the delta to minutes and round to 2 decimal places
            self.delta_minutes = round(delta.total_seconds() / 60, 2)

    def __eq__(self, other):
        if isinstance(other, TimeData):
            return (self.start_time_string == other.start_time_string and
                    self.end_time_string == other.end_time_string)
        return False

    def __hash__(self):
        return hash((self.start_time_string, self.end_time_string))
