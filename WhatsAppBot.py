from os import getenv
from heyoo import WhatsApp
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    load_dotenv()

    messenger = WhatsApp(token=getenv("WHATSAPP_TOKEN"), phone_number_id=getenv("WHATSAPP_PHONE_NUMBER_ID"))

    response = messenger.send_message(message="hi https://www.youtube.com/watch?v=K4TOrB7at0Y", recipient_id="972548826569")

    print(response)