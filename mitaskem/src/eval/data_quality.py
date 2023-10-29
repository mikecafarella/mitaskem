import json
import os

from mitaskem.src.connect import get_gpt4_match

def get_mit_variable_eval_prompt(extraction, grdthruth):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/mit_variable_eval_prompt.txt'), "r")
    prompt = text_file.read()
    print(prompt)
    text_file.close()

    prompt = prompt.replace("[EXTRACT]", extraction)
    prompt = prompt.replace("[GROUND]", grdthruth)
    print(prompt)
    return prompt

def evaluate_variable_extraction(extraction, grdthruth, gpt_key):
    prompt = get_mit_variable_eval_prompt(extraction, grdthruth)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4")
    print(ans)
    return ans

def load_concise_vars(input_file_str):
    # Read JSON data from the file
    json_data = json.loads(input_file_str)
    str = ""
    for item in json_data['attributes']:
        if 'id' not in item['payload']:
            continue
        variable_id = item['payload']['id']['id']
        variable_name = item['payload']['names'][0]['name']
        value = item['payload']['descriptions'][0]['source']
        output_line = f"{variable_id}, {variable_name}: {value}\n"
        str += output_line
    return str

def get_mit_model_card_eval_prompt(extraction, grdthruth):
    text_file = open(os.path.join(os.path.dirname(__file__), '../prompts/mit_model_card_eval_prompt.txt'), "r")
    prompt = text_file.read()
    print(prompt)
    text_file.close()

    prompt = prompt.replace("[EXTRACT]", extraction)
    prompt = prompt.replace("[GROUND]", grdthruth)
    print(prompt)
    return prompt

def evaluate_model_card_extraction(extraction, grdthruth, gpt_key):
    prompt = get_mit_model_card_eval_prompt(extraction, grdthruth)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4")
    print(ans)
    return ans


if __name__ == "__main__":
    GPT_KEY = None
    key = GPT_KEY
    cache_dir = "/Users/chunwei/research/mitaskem/resources/xDD/"

    res_mit_file = "mit-extraction/bucky__mit-extraction_id.json"

    ground_truth = "../../resources/models/Bucky/bucky_variables.txt"

    mit_concise = res_mit_file.replace(".json", "-concise.txt")
    # print("file exist: ", os.path.isfile("/tmp/askem/" + res_mit_file))
    load_concise_vars(
        os.path.join(cache_dir, res_mit_file),
        os.path.join(cache_dir, mit_concise))
    mit_text = open(os.path.join(cache_dir, mit_concise)).read()

    res_arizona_file = "arizona-extraction/bucky_arizona_output_example.json"
    arizona_concise = res_arizona_file.replace(".json", "-concise.txt")
