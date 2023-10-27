from server import app
import os
GPT_KEY = os.environ.get('OPENAI_API_KEY')
from fastapi.testclient import TestClient
import json 
test_papers = [
        '../../resources/models/Bucky/bucky.txt',
    # './text_ijerph-18-09027.txt',
    # './text_s41598-022-06159-x.txt',
    # 'text_shakari-wastewater.txt',
]

def run_test(paper_path):
    client = TestClient(app)

    with open(paper_path, 'rb') as f:

        response = client.post('/annotation/upload_file_extract', params={"gpt_key": GPT_KEY}, 
                    files={'file':('filename', f)})
        
        pretty = json.dumps(response.json(), indent=2)
        print('response:\n', pretty)


for p in test_papers:
    print(f'Test: {p}')
    run_test(p)
