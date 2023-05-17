
import os
import runpod
import importlib
from . import prompt

position = os.path.dirname(__file__)
model_tokenizer = {'model' : None}

runpod.api_key = os.getenv('RUNPOD_API')
endpoint = runpod.Endpoint("es8q9vhxv28pzm")

def get_model_tokenizer(model_tok: dict = dict()):
    return model_tok

def process(prompt, *args, **kwargs):
    run_request = endpoint.run(
        {"prompt" : prompt, 'CHECK': 'PING', **kwargs}
    )

    # Check the status of the endpoint run request
    print(run_request.status())

    # Get the output of the endpoint run request, blocking until the endpoint run is complete.
    result = run_request.output()
    return result.get('result', '')

def get_conversation():
    conversations = importlib.reload(prompt)
    return conversations.convo

if __name__ == '__main__':
    print(process("USER: can you surf the web?\nASSISTANT(Ron):"))