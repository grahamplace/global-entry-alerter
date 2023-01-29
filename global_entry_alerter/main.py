import argparse
import logging
import sys
import time
from global_entry_alerter.clients.twilio import TwilioClient
from global_entry_alerter.clients.scheduler import SchedulerClient, Location
import tomllib

logging.basicConfig(
    format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%d-%b-%y %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _run(test_mode: bool = False):
    if test_mode:
        logger.warning("Running in test mode. Alerts will not be sent.")

    with open("config.toml", mode="rb") as fp:
        config = tomllib.load(fp)
        locations = [
            Location(name=loc["name"], code=loc["code"])
            for loc in config["fetching"]["locations"]
        ]
        logger.info(f"Running with config: {config}")

    twilio_client = TwilioClient()
    scheduler_client = SchedulerClient(config["fetching"]["lookahead_weeks"], locations)

    sent_messages = []
    while True:
        messages = scheduler_client.fetch_all()
        new_messages = [m for m in messages if m not in sent_messages]

        logger.info(f"{len(messages)} total, {len(new_messages)} new")
        if not test_mode:
            twilio_client.send_messages(new_messages, config["sending"]["to_numbers"])

        sent_messages.extend(messages)

        time.sleep(config["fetching"]["wait_seconds"])


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", "-t", action="store_true", default=False)
    args = parser.parse_args()
    _run(args.test)


if __name__ == "__main__":
    run()
