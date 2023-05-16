
import ast, json, requests, os

import gpt_key
from connect import get_mit_arizona_var_prompt, get_gpt4_match
from dataset_id import modify_dataset
from ensemble.ensemble import load_paper_info, extract_variables
from gpt_key import *
PARAM = "/Users/chunwei/research/mitaskem/resources/xDD/params/"
API_ROOT = "http://0.0.0.0:8000/"

def load_concise_vars(input_file, o_file):
    # Read JSON data from the file
    with open(input_file, 'r') as file:
        json_data = json.load(file)

    # Open a new file to write the output
    with open(o_file, 'w') as output_file:
        # Extract id, name, and text_annotations for each variable
        for variable in json_data:
            id = variable['id']
            name = variable['name']
            text_annotations = variable['text_annotations']
            output_line = f"{id}, {name}: {text_annotations}\n"

            # Write the extracted information to the output file
            output_file.write(output_line)


def build_map_from_concise_vars(mit, arizona):
    prompt = get_mit_arizona_var_prompt(mit, arizona)
    ans = get_gpt4_match(prompt, GPT_KEY, model="gpt-4")
    return ans

def mit_extraction(paper):
    extract_variables(
        "/Users/chunwei/research/mitaskem/resources/xDD/paper/" + paper["title"] + ".txt",
        "/Users/chunwei/research/mitaskem/resources/xDD/params")

    with open(PARAM + paper["title"] + "_vars.txt", "r") as f:
        text = f.read()
        dct_extract = {"text": text, "gpt_key": GPT_KEY}
        json_str = requests.post(API_ROOT + "annotation/find_text_vars/", params=dct_extract).text

    print(json_str)
    dkg_json = json.loads(json_str)
    for variable in dkg_json:
        variable["title"] = paper["title"]
        variable["doi"] = paper["doi"]
        variable["url"] = paper["url"]
    dkg_json_string = json.dumps(dkg_json)
    print(dkg_json_string)

    dir = "/Users/chunwei/research/mitaskem/resources/dataset/ensemble/"
    # with open(os.path.join(dir,"headers.txt"), "w+") as fw:
    #     for filename in os.listdir(dir):
    #         file = os.path.join(dir, filename)
    #         if os.path.isfile(file) and file.endswith(".csv"):
    #             fw.write("{}:\t{}".format(filename, open(file, "r").readline()))

    with open(os.path.join(dir, "headers.txt")) as f:
        dataset_str = f.read()
        print(dataset_str[:419])

    from connect import vars_dataset_connection

    json_str, success = vars_dataset_connection(dkg_json_string, dataset_str, GPT_KEY)
    print(json_str)

    data_json = json.loads(json_str)

    # %%
    with open(
            "/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/" + paper["title"] + '__mit-extraction.json',
            'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    # %% md

    load_concise_vars(
        "/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/" + paper["title"] + '__mit-extraction.json',
        "/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/" + paper["title"] + '__mit-concise.txt')

    # generate json with dataset id in file "filename__mit-extraction_id.json"
    modify_dataset(
        '/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/' + paper["title"] + '__mit-extraction.json',
        '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/headers.txt',
        '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/catalog.txt')






if __name__ == "__main__":
    papers = load_paper_info("/Users/chunwei/research/mitaskem/resources/xDD/xdd_paper.json")
    paper = papers[6]  # 0 1 4 6
    print(paper)

    # mit_extraction(paper)
    mit_text = open('/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/' + paper["title"] + '__mit-concise.txt',
                    "r").read()
    arizona_text = open('/Users/chunwei/research/mitaskem/resources/xDD/arizona-extraction/variables_' + paper["title"] + '.txt',
                    "r").read()

    # mit_arizona_map = build_map_from_concise_vars(mit_text, arizona_text)
    # open('/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/' + paper["title"] + '__map.txt', "w").write(mit_arizona_map)

    modify_dataset(
        '/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/'+paper["title"]+'__mit-extraction.json',
        '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/headers.txt',
        '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/catalog.txt')

