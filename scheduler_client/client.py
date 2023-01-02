from datetime import datetime, timedelta
import requests
from typing import List
from collections import namedtuple

URL = "https://ttp.cbp.dhs.gov/schedulerapi/locations/{location}/slots?startTimestamp={start}&endTimestamp={end}"
TTP_TIME_FORMAT = "%Y-%m-%dT%H:%M"

NOTIF_MESSAGE = "{location}: {date}"
MESSAGE_TIME_FORMAT = "%A, %B %d, %Y at %I:%M %p"

Location = namedtuple("Location", ["name", "code"])


class SchedulerException(Exception):
    pass


class SchedulerClient:
    def __init__(self, weeks: int, locations: List[Location]):
        self.weeks = weeks
        self.locations = locations

    def fetch_for_location(self, location: Location) -> List[str]:
        start = datetime.now()
        end = start + timedelta(weeks=self.weeks)

        url = URL.format(
            location=location.code,
            start=start.strftime(TTP_TIME_FORMAT),
            end=end.strftime(TTP_TIME_FORMAT),
        )

        try:
            results = requests.get(url).json()
        except ConnectionError as e:
            raise SchedulerException("Could not connect to scheduler API") from e

        messages = []
        for result in results:
            if result["active"] > 0:
                timestamp = datetime.strptime(result["timestamp"], TTP_TIME_FORMAT)
                messages.append(
                    NOTIF_MESSAGE.format(
                        location=location.name,
                        date=timestamp.strftime(MESSAGE_TIME_FORMAT),
                    )
                )

        return messages

    def fetch_all(self) -> List[str]:
        results = []
        for location in self.locations:
            results.extend(self.fetch_for_location(location))

        return results
