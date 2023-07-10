import os
import openai

## assumes OPENAI_API_KEY is set
# can add this to bashrc to load from file rather than paste in terminal
# export OPENAI_API_KEY=$(cat ~/.openaikey)
openai.api_key = os.getenv('OPENAI_API_KEY')
GPT_KEY = openai.api_key # some files assume this