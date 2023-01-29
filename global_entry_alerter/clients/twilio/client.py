import os
import logging
from twilio.rest import Client
from typing import List

logger = logging.getLogger(__name__)
twilio_logger = logging.getLogger("twilio")
twilio_logger.setLevel(logging.WARNING)


class TwilioException(Exception):
    pass


class TwilioClient:
    def __init__(self):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        if account_sid is None or not account_sid:
            raise TwilioException("TWILIO_ACCOUNT_SID env var not set")

        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        if auth_token is None or not auth_token:
            raise TwilioException("TWILIO_AUTH_TOKEN env var not set")

        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        if from_number is None or not from_number:
            raise TwilioException("TWILIO_PHONE_NUMBER env var not set")

        self.from_number = from_number
        self.client = Client(account_sid, auth_token)

    def send_sms(self, body: str, to_number: str):
        if not body or body is None:
            raise TwilioException("Message body cannot be empty")
        if not to_number or to_number is None:
            raise TwilioException("Message to_number cannot be empty")

        logger.info(f"Sending sms to {to_number}:  {body}")
        self.client.messages.create(body=body, from_=self.from_number, to=to_number)

    def send_messages(self, messages: List[str], to_numbers: List[str]):
        if not messages:
            return

        # 1600-character limit on SMS, so break full list into smaller lists
        chunks = list(chunkify(messages, 10))
        logger.info(f"Sending {len(messages)} messages as {len(chunks)} texts")

        for c in chunks:
            body = "\n\n".join([str(t) for t in c])
            for number in to_numbers:
                self.send_sms(body, number)


def chunkify(full_list, n):
    for i in range(0, len(full_list), n):
        yield full_list[i : i + n]
