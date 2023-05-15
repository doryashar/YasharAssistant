
import os
from llama_cpp import Llama
position = os.path.dirname(__file__)
stop = '### '
model_tokenizer = {'model' : None}
def get_model_tokenizer(model_tok: dict = dict()):
    print('getting model')
    llm = Llama(model_path=os.path.join(position,"ggml-vic13b-q4_0.bin"), n_ctx=5 * 1024)
    model_tokenizer['model'] = model_tok['model'] = llm
    return model_tok

def process(prompt, max_tokens=256, stop=stop, echo=False, stream=True, *args, **kwargs):
    if not model_tokenizer['model'] or not model_tokenizer['tokenizer']:
        return 'Model/Tokenizner yet to be set-up'    

    model = model_tokenizer['model']
    result = model(prompt, max_tokens=max_tokens, stop=stop, echo=echo, stream=stream)
    
    output = ''.join([word["choices"][0]["text"] for word in result])
    return output
    
