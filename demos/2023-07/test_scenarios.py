import openai
from gpt_key import GPT_KEY
from server import app
from fastapi.testclient import TestClient


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
        
        print(response.text)


for p in test_papers:
    print(f'Test: {p}')
    run_test(p)
