import logging
import sys
import time
from twilio_client import TwilioClient
from scheduler_client import SchedulerClient, Location
import tomllib

LOGGING_FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO, stream=sys.stdout)


def main():
    with open("config.toml", mode="rb") as fp:
        config = tomllib.load(fp)
        locations = [
            Location(name=loc["name"], code=loc["code"])
            for loc in config["fetching"]["locations"]
        ]

    twilio_client = TwilioClient()
    scheduler_client = SchedulerClient(config["fetching"]["lookahead_weeks"], locations)

    sent_messages = []
    while True:
        messages = scheduler_client.fetch_all()
        new_messages = [m for m in messages if m not in sent_messages]

        logging.info(f"{len(messages)} total, {len(new_messages)} new")
        twilio_client.send_messages(new_messages, config["sending"]["to_numbers"])
        sent_messages.extend(messages)

        time.sleep(config["fetching"]["wait_seconds"])


if __name__ == "__main__":
    main()
