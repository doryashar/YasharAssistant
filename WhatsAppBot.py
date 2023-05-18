import logging  

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


from os import getenv
from heyoo import WhatsApp
from dotenv import load_dotenv
import os
from flask import Flask, request, make_response
from agent import Agent
import asyncio, httpx

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
queue = asyncio.Queue()
    
# Initialize Flask App
app = Flask(__name__)

# async def handle_items():
#     while True:
#         message, mobile, name = await queue.get()
#         agent.get_chat(name, mobile)
#         reply_text = await agent.chat(mobile, message) 
#         messenger.send_message(reply_text, mobile) # Add await 
#         queue.task_done()
async def handle_items():
    while True:
        data = await queue.get()
        handle_data(data)
        queue.task_done()
        

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
                logging.info("Message: %s", message)
                # await queue.put((message, mobile, name))

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
@app.route('/sayname')
def sayname():
    asyncio.create_task(handle_items)
    return '<h1>Hello Flask</h1>'

@app.get("/")
def verify_token():
    if request.args.get("hub.verify_token") == getenv('FLASK_VERIFY_TOKEN'):
        logging.info("Verified webhook")
        response = make_response(request.args.get("hub.challenge"), 200)
        response.mimetype = "text/plain"
        return response
    logging.error("Webhook Verification failed")
    return "Invalid verification token"

@app.post("/")
async def hook(): 
    # Handle Webhook Subscriptions
    data = request.get_json()
    logging.info("Received webhook data: %s", data)
    await queue.put(data)
    return "OK", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
# if __name__ == "__main__":
#     load_dotenv()
#     messenger = WhatsApp(token=getenv("WHATSAPP_TOKEN"), phone_number_id=getenv("WHATSAPP_PHONE_NUMBER_ID"))
#     response = messenger.send_message(message="hi https://www.youtube.com/watch?v=K4TOrB7at0Y", recipient_id="972548826569")
#     print(response)
