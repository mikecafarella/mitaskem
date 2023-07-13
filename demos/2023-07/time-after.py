# import sys
# srcpath = '/Users/orm/repos/mitaskem/src'
# askempath = '/Users/orm/repos/mitaskem'
# sys.path.append(askempath)
# sys.path.append(srcpath)

import os
import openai
from mit_extraction import async_mit_extraction_restAPI
import asyncio

bucky_path = os.path.abspath('../resources/models/Bucky/bucky.txt')
res = asyncio.run(async_mit_extraction_restAPI('/tmp/askemcache/bucky.txt', gpt_key=openai.api_key, cache_dir='/tmp/askemcache/'))

print('result:', res)

