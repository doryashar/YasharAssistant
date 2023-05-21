import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

import asyncio
from os import getenv
from heyoo import WhatsApp
from dotenv import load_dotenv
import os
from agent import Agent



# # function converted to coroutine
# async def get_xkcd_image(session):
#     random = randint(0, 300)
#     result = await session.get(f'http://xkcd.com/{random}/info.0.json') # dont wait for the response of API
#     return result.json()['img']

# # function converted to coroutine
# async def get_multiple_images(number):
#     async with httpx.AsyncClient() as session: # async client used for async functions
#         tasks = [get_xkcd_image(session) for _ in range(number)]
#         result = await asyncio.gather(*tasks, return_exceptions=True) # gather used to collect all coroutines and run them using loop and get the ordered response
#     return result


# Load .env file
load_dotenv()
messenger = WhatsApp(os.getenv("WHATSAPP_TOKEN"), phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
agent = Agent() 
known_ids: set()

async def handle_message(message, from_mobile, from_name):
    logging.info("Message: %s", message)
    reply_text = await agent.chat(from_mobile, message) 
    logging.info(f"Sending {reply_text} to {from_mobile}")
    messenger.send_message(reply_text, from_mobile) # Add await 
    
# async 
async def handle_data(data):
    changed_field = messenger.changed_field(data)
    if changed_field == "messages":
        new_message = messenger.is_message(data)
        if new_message:
            mobile = messenger.get_mobile(data)
            name = messenger.get_name(data)
            message_type = messenger.get_message_type(data)
            logging.info(f"New Message; sender:{mobile} name:{name} type:{message_type}")
            if message_type == "text":
                message = messenger.get_message(data)
                mid = data.get('entry')[0]['id']
                if mid in known_ids:
                    logging.error('id already used')
                    return
                known_ids.add(mid)
                await handle_message(message, mobile, name)
                return

            elif message_type == "interactive":
                message_response = messenger.get_interactive_response(data)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logging.info(f"Interactive Message; {message_id}: {message_text}")

            elif message_type == "location":
                message_location = messenger.get_location(data)
                message_latitude = message_location["latitude"]
                message_longitude = message_location["longitude"]
                logging.info("Location: %s, %s", message_latitude, message_longitude)

            elif message_type == "image":
                image = messenger.get_image(data)
                image_id, mime_type = image["id"], image["mime_type"]
                image_url = messenger.query_media_url(image_id)
                image_filename = messenger.download_media(image_url, mime_type)
                logging.info(f"{mobile} sent image {image_filename}")

            elif message_type == "video":
                video = messenger.get_video(data)
                video_id, mime_type = video["id"], video["mime_type"]
                video_url = messenger.query_media_url(video_id)
                video_filename = messenger.download_media(video_url, mime_type)
                logging.info(f"{mobile} sent video {video_filename}")

            elif message_type == "audio":
                audio = messenger.get_audio(data)
                audio_id, mime_type = audio["id"], audio["mime_type"]
                audio_url = messenger.query_media_url(audio_id)
                audio_filename = messenger.download_media(audio_url, mime_type)
                logging.info(f"{mobile} sent audio {audio_filename}")

            elif message_type == "document":
                file = messenger.get_document(data)
                file_id, mime_type = file["id"], file["mime_type"]
                file_url = messenger.query_media_url(file_id)
                file_filename = messenger.download_media(file_url, mime_type)
                logging.info(f"{mobile} sent file {file_filename}")
            else:
                logging.info(f"{mobile} sent {message_type} ")
                logging.info(data)
        else:
            delivery = messenger.get_delivery(data)
            if delivery:
                logging.info(f"Message : {delivery}")
            else:
                logging.info("No new message")
 