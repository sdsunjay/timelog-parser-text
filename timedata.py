from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class TimeData:
    start_time_string: str
    end_time_string: str
    date_format: str
    start_time_utc: datetime = field(init=False)
    end_time_utc: datetime = field(init=False)
    delta_minutes: float = field(init=False)

    def __post_init__(self):
        try:
            self.start_time_utc = datetime.strptime(self.start_time_string.strip(), self.date_format).astimezone(timezone.utc)
            self.end_time_utc = datetime.strptime(self.end_time_string.strip(), self.date_format).astimezone(timezone.utc)
        except ValueError as e:
            print(f"Error parsing date strings: {e}")
            self.delta_minutes = None
            return

        # Ensure end time is not earlier than start time
        if self.end_time_utc < self.start_time_utc:
            print(f"Error: {self.end_time_string} ({self.end_time_utc}) is earlier than {self.start_time_string} ({self.start_time_utc}).")
            self.delta_minutes = None
        else:
            # Calculate the delta between the two times
            delta = self.end_time_utc - self.start_time_utc
            # Convert the delta to minutes and round to 2 decimal places
            self.delta_minutes = round(delta.total_seconds() / 60, 2)

    def __eq__(self, other):
        if isinstance(other, TimeData):
            return (self.start_time_string.strip() == other.start_time_string.strip() or
                    self.end_time_string.strip() == other.end_time_string.strip())
        return False

    def __hash__(self):
        return hash(self.start_time_string.strip())


    def __lt__(self, other):
        if isinstance(other, TimeData):
            return self.start_time_utc < other.start_time_utc
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, TimeData):
            return self.start_time_utc <= other.start_time_utc
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, TimeData):
            return self.start_time_utc > other.start_time_utc
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, TimeData):
            return self.start_time_utc >= other.start_time_utc
        return NotImplemented
