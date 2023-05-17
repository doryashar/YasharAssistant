import asyncio
import os
import threading, time
import logging
# from whispercpp import Whisper

# result = w.transcribe("myfile.mp3")
# text = w.extract_text(result)
# output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=True)
import prompts.vicuna13b11
import importlib
import os

MODEL_NAME = 'wizard-vicuna-runpod' #'vicuna-llama-cpp'

class Agent:
    max_id = 0
    recreate_conversation_on_repeated_starts = True
    
    def __init__(self, name = 'Rona') -> None:
        self.in_process = dict()
        self.stop = '</s>'
        self.name = name
        # self.whisper = Whisper('tiny')
        self.download_model(async_get=False)
        os.makedirs('conversations', exist_ok=True)

    def download_model(self, model = MODEL_NAME, async_get=True):
        logging.info(f'Getting model and tokenizer from: {model}')
        
        self.model = importlib.import_module('models.' + model + '.model')
        model_tok = dict()
        
        if async_get:
            ret = threading.Thread(target=self.model.get_model_tokenizer, args=(model_tok,))
            ret.start()
        else:
            self.model.get_model_tokenizer(model_tok)
            ret = None
        return model_tok, ret
    
    def process(self, X):
        logging.info(f"processing {X}")
        t_1 = time.time()
        res = self.model.process(X)
        t_2 = time.time()
        return res
    
    def get_log_path(self, id) -> tuple[str, bool]:
        path = os.path.abspath(f'conversations/{id}.log')
        return path, os.path.exists(path)
    
    def get_chat(self, user_name, nid=None):
        logging.info(f'Getting chat path for: {user_name}, nid:{nid}')
        if nid:
            path, exists = self.get_log_path(nid)
            if exists: return path
        return self.get_log_path(self.start_chat(user_name, nid))
        
    def start_chat(self, user_name = 'USER', nid = None):
        id = nid if nid else Agent.max_id
        
        path, exists = (None, None)
        while True:
            path, exists = self.get_log_path(id)
            if not (exists and (not self.recreate_conversation_on_repeated_starts or not nid)):
                break
            id += 1
        
        if not exists:
            conversations = importlib.reload(prompts.vicuna13b11)
            with open(path,'w') as fw:
                # with open('prompts/vicuna13b1.1.py') as fr: fr.read()
                    fw.write(user_name  + '\n' + conversations.convo.format(USER=user_name, ASSISTANT=self.name, STOP=self.stop))
        return id
    
    async def chat(self, user_id: str, text: str) -> str:
        conv_log_path, exists = self.get_log_path(user_id)
        if not exists:
            self.start_chat(id=user_id)
        
        history = ''
        with open(conv_log_path, 'r') as fd:
            USER = fd.readline().strip()
            history = fd.read()
        
        prompt = f"\n{self.stop}{USER}: {text.replace(self.stop, ',')}\n{self.stop}{self.name}:"
        q = history + prompt
        
        response = await self.process_text(q)
            
        with open(conv_log_path, 'a') as fd:
            full_response = prompt + response
            fd.write(full_response)
        return response
            
    async def process_text(self, text: str) -> str:
        output = self.process(text)
        # output = output["choices"][0]["text"]
        
        logging.info(text, output)
        return output

async def main():
    agent = Agent('Ronit')
    
    # question = "Name the planets in the solar system?"
    # question = "translate to hebrew: 'i would like to thank you, mister. you are pretty horrible'"
    # question = "write a happy birthday wish to my father, his name is ohad and he is 64 years old. he has 2 boys and a girl: Dor, Omri and Ofir. he loves swimming and hang with his wife, Sari"
    question1 = 'Hi! are you single?'
    question2 = 'because i dont like single people'
    
    uid = agent.start_chat('Dor', 0)
    logging.info('chat started')
    await agent.chat(uid, question1)
    # await agent.chat(uid, question2)
    
if __name__ == '__main__':
    asyncio.run(main())