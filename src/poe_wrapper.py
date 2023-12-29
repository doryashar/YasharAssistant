# TOKEN = "vgqNX2m2tV9W7WhF7Sa3Gw=="
# from poe_api_wrapper import PoeApi
# client = PoeApi(TOKEN, proxy=False)
# history = client.get_chat_history()


## ======================================================================================= ##

# from __future__ import annotations
# from typing import AsyncIterable
# from modal import Image, Stub, asgi_app
# from fastapi_poe import PoeBot, make_app
# from fastapi_poe.client import stream_request
# from fastapi_poe.types import (
#     PartialResponse,
#     QueryRequest,
#     SettingsRequest,
#     SettingsResponse,
# )

# class GPT35TurboBot(PoeBot):
#     async def get_response(self, query: QueryRequest) -> AsyncIterable[PartialResponse]:
#         async for msg in stream_request(query, "GPT-3.5-Turbo", query.access_key):
#             yield msg

#     async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
#         return SettingsResponse(
#             server_bot_dependencies={"GPT-3.5-Turbo": 1}
#         )
    
# REQUIREMENTS = ["fastapi-poe==0.0.23"]
# image = Image.debian_slim().pip_install(*REQUIREMENTS)
# stub = Stub("turbo-test-poe-bot")

# @stub.function(image=image)
# @asgi_app()
# def fastapi_app():
#     bot = GPT35TurboBot()
#     app = make_app(bot, allow_without_key=True)
#     return app

## ======================================================================================= ##

# import asyncio
# from fastapi_poe.types import ProtocolMessage
# from fastapi_poe.client import get_bot_response

# # Create an asynchronous function to encapsulate the async for loop
# async def get_responses(api_key):
#     message = ProtocolMessage(role="user", content="Hello world")
#     async for partial in get_bot_response(messages=[message], bot_name="GPT-3.5-Turbo", api_key=api_key):
#         print(partial)

# # Replace <api_key> with your actual API key, ensuring it is a string.
# TOKEN = "Lgu-hUygTNv6Vbh1OcdTO"
# api_key = "<missing>"

# # Run the event loop
# # For Python 3.7 and newer
# asyncio.run(get_responses(api_key))

# # For Python 3.6 and older, you would typically do the following:
# # loop = asyncio.get_event_loop()
# # loop.run_until_complete(get_responses(api_key))
# # loop.close()