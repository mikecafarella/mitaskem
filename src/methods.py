import tiktoken
import asyncio
from typing import List
import openai ## already inited
## assumes 

from openai import OpenAIError

import re
def clean_spaces(text):
    text1 = re.sub(' +', ' ', text)
    text2 = re.sub('\n+', '\n', text1)
    return text2

def strip_latex_preamble(text):
    start = text.find('\\begin{document}')
    end_marker = '\\end{document}'
    end = text.find(end_marker)
    end_len = len(end_marker)
    return text[start:end+end_len]


_context_lengths = {
    'text-davinci-002':4097,
    'text-davinci-003':4097,
    'gpt-3.5-turbo-16k':16000, ## may be slightly larger
    'gpt-3.5-turbo':4097,
    'gpt-4':8000,
}

def split_into_chunks(text_tokens, max_chunk_size_tokens : int):
    """ 
    split tokens into chunks of at most max size tokens
    """
    token_splits = []
    curr_pos = 0
    while curr_pos < len(text_tokens):
        split = text_tokens[curr_pos:curr_pos + max_chunk_size_tokens]
        token_splits.append(split)
        curr_pos += max_chunk_size_tokens

    assert sum(token_splits, []) == text_tokens
    for c in token_splits:
        assert len(c) <= max_chunk_size_tokens
    return token_splits


def create_prompt_tasks(prompt, document, model_name, answer_token_length=256, chunk_token_length=None):
    max_context_length = _context_lengths[model_name]
    if chunk_token_length is None:
        chunk_token_length = max_context_length - answer_token_length

    tokenizer = tiktoken.encoding_for_model(model_name)
    
    pre_text, post_text = prompt.split('[TEXT]')
    pre_tok, post_tok = tokenizer.encode_batch([pre_text, post_text])
    available_length = chunk_token_length - len(pre_tok) - len(post_tok) - 2 # space before and after 
    text_tokens = tokenizer.encode(document)

    assert available_length > 0
    chunks = split_into_chunks(text_tokens, max_chunk_size_tokens=available_length)
    text_tasks  = tokenizer.decode_batch([pre_tok + chunk + post_tok for chunk in chunks])
    return text_tasks

async def fork_join_requests(prompts, model : str):
    """
    send one request per prompt 
    """

    chat_completion_models = ['gpt-3.5-turbo-16k','gpt-3.5-turbo', 'gpt-4']
    
    acc = []
    for prompt in prompts:
        if model in chat_completion_models:
            # TODO: chat completions lets one split the prompt.
            cor = openai.ChatCompletion.acreate(model=model, 
                                                messages=[
                                                    #{"role":"system", "content":TODO}
                                                    {"role": "user", "content": prompt},
                                                ],
                                                temperature=0.0)
        else:
            cor = openai.Completion.acreate(model=model, prompt=prompt, 
                                            temperature=0.0, max_tokens=256)
            
        acc.append(asyncio.create_task(cor))

    outputs = []
    for cor in acc:        
        try:        
            response = await cor
        except OpenAIError as err:   
            return f"OpenAI connection error: {err}", False

        if model in chat_completion_models:
            result = response.choices[0].message.content.strip()
        else:
            result = response.choices[0].text.strip()
        outputs.append(result)

    return outputs