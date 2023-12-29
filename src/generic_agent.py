import asyncio
import os
import threading, time
import logging
# from whispercpp import Whisper

# result = w.transcribe("myfile.mp3")
# text = w.extract_text(result)
# output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=True)
# import prompts.vicuna13b11
import importlib
import os


class BaseAgent:
    MODEL_NAME = 'BaseModel'
    max_id = 0
    
    def __init__(self, agent_name = '{ASSISTANT}') -> None:
        self.name = agent_name
        os.makedirs('conversations', exist_ok=True)
        
        self.user_names = dict()
        with open('user_names.txt', 'r') as fd:
            for line in fd.readlines():
                user_id, name = line.strip().split(':')
                self.user_names[user_id] = name
        
        self.prompt = '{history}\n{user_name}:{message}'
        self.model = self.get_model(self.MODEL_NAME, async_get=False)
        # self.stop = '</s>'
        # self.in_process = dict()
        # self.whisper = Whisper('tiny')
        # self.download_model(async_get=False)

    def get_model(self, model = MODEL_NAME, async_get=True):
        # logging.debug(f'Getting model and tokenizer from: {model}')
        pass

    def get_log_path(self, id) -> tuple[str, bool]:
        path = os.path.join(os.path.abspath('conversations'), f'{id}.log')
        return path, os.path.exists(path)
    
    def get_history(self, user_id):
            conv_log_path, exists = self.get_log_path(user_id)
            if not exists:
                return ''
            with open(conv_log_path, 'r') as fd:
                USER = fd.readline().strip()
                history = fd.read()
                return history
    
    def update_history(self, user_id, prompt, response, user_name=None):
            if not user_name:
                user_name = self.get_user_name(user_id)
            conv_log_path, exists = self.get_log_path(user_id)
            with open(conv_log_path, 'w') as fd:
                fd.write(f"{user_name}\n{prompt}\n{response}")
                fd.flush()
                
    def preprocess_text(self, text):
        return text
    
    def postprocess_text(self, user_id, prompt, response, finish_callbacks, *args, **kwargs):
        return response, args, kwargs
    
    def get_user_name(self, user_id):
        return self.user_names.get(user_id, '{USER}')
    
    async def chat(self, user_id: str, text: str, use_history=True, finish_callbacks=[], *args, **kwargs) -> str:
        user_name = self.get_user_name(user_id)
        
        if use_history:
            history = self.get_history(user_id)
        else:
            history = ''
            
        message = self.preprocess_text(text)
        prompt = self.prompt.format(message=message, user_name=user_name, history=history)
        response = await self.process_text(prompt, *args, **kwargs)
        
        self.update_history(user_id, prompt, response, user_name)
        response, args, kwargs = self.postprocess_text(user_id, prompt, response, finish_callbacks, *args, **kwargs)
        
        for finish_callback in finish_callbacks:
            args, kwargs = finish_callback(prompt=prompt, response=response, *args, **kwargs)
        return response, args, kwargs
            
    async def process_text(self, text: str) -> str:
        t1 = time.time()
        time.sleep(1)
        output = "RESPONSE"
        t2 = time.time()
        logging.debug((text, output, t2-t1))
        return output

async def main():
    logging.basicConfig(level=logging.DEBUG)
    agent = BaseAgent('Ronit')
    
    # question = "Name the planets in the solar system?"
    # question = "translate to hebrew: 'i would like to thank you, mister. you are pretty horrible'"
    # question = "write a happy birthday wish to my father, his name is ohad and he is 64 years old. he has 2 boys and a girl: Dor, Omri and Ofir. he loves swimming and hang with his wife, Sari"
    question1 = 'Hi! are you single?'
    question2 = 'because i dont like single people'
    
    # uid = agent.start_chat('Dor', 0)
    # logging.debug('chat started')
    res = await agent.chat('0', question1)
    logging.info(f"\nQ: {question1}\nResponse: {res}")
    # await agent.chat(uid, question2)
    
if __name__ == '__main__':
    asyncio.run(main())