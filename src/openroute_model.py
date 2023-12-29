#TODO:
# Translate

import requests
import json
import dotenv
import os
import asyncio
import functools
import logging
from src.generic_agent import BaseAgent

dotenv.load_dotenv()
model_to_load = os.getenv("OPENROUTE_MODEL", "mistralai/mistral-7b-instruct")  # Optional
completion_url = "https://openrouter.ai/api/v1/chat/completions"
headers={
    "HTTP-Referer": os.getenv("YOUR_APP_URL", "TEST"), # Optional, for including your app on openrouter.ai rankings. 
    "X-Title": os.getenv("YOUR_APP_NAME", "TEST"), # Optional. Shows in rankings on openrouter.ai.
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv("OPENROUTER_API_KEY"),
}

class OpenRouteAgent(BaseAgent):
    MODEL_NAME = model_to_load
    def __init__(self, agent_name = 'Rona') -> None:
        super().__init__(agent_name)
        self.http_post_func = functools.partial(requests.post, headers=headers, timeout=10)
        self.prompt = '{history}\n{message}'
    async def process_text(self, text: str, use_async=False) -> str:
        """
        Asynchronously handles a message.

        Args:
            message (Any): The message to be handled.
            from_mobile (bool): Indicates whether the message is from a mobile device.
            from_name (str): The name of the sender.

        Returns:
            Any: The response from the message handling operation.
        """
        
        loop = asyncio.get_event_loop()
        content = text
        data = {
            "messages": [
            {"role": "user", "content": content}
            ]
        }
        
        if model_to_load:
            data["model"] = model_to_load
        
        logging.debug(f'Sending: {data} to {completion_url}')
        if use_async:
            future = loop.run_in_executor(None, self.http_post_func, completion_url, json.dumps(data))
            response = await future
        else:
            response = self.http_post_func(completion_url, json.dumps(data))
            
        if response.status_code == 200:
            resp_data = json.loads(response.text)
            return resp_data["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")