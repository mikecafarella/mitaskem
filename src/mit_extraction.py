
import ast, json, requests, os

import gpt_key
from connect import get_mit_arizona_var_prompt, get_gpt4_match
from dataset_id import modify_dataset
from ensemble.ensemble import load_paper_info, extract_variables, extract_vars
from gpt_key import *
from text_search import text_var_search, vars_dedup, vars_to_json
from connect import vars_dataset_connection

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


def find_vars_from_text(text: str, gpt_key: str):
    length = len(text)
    segments = int(length / 1000 + 1)

    outputs = ""

    for i in range(segments):
        snippet = text[i * 1000: (i + 1) * 1000]
        s, success = text_var_search(text=snippet, gpt_key=gpt_key)

        if not success:
            return f"""Error: {s}"""

        outputs += s
        # print(outputs)

    return ast.literal_eval(vars_to_json(vars_dedup(outputs)))

def mit_extraction_restAPI(file_name, gpt_key, cache_dir="/tmp/askem"):
    paper_name = file_name.split(".txt")[0]
    org_file = os.path.join(cache_dir, file_name)
    print("is file existing", os.path.exists(org_file))
    extract_vars(org_file, cache_dir)
    file_path = os.path.join(cache_dir, paper_name+"_vars.txt")
    print(file_path)
    with open(file_path, "r") as f:
        text = f.read()
        json_str = find_vars_from_text(text, gpt_key)
        print(type(json_str))

    dkg_json = json.loads(json.dumps(json_str))
    for variable in dkg_json:
        variable["title"] = paper_name
    dkg_json_string = json.dumps(dkg_json)
    print(dkg_json_string)
    dirname = os.path.dirname(__file__)
    dir = os.path.join(dirname, '../resources/dataset/ensemble')
    # dir = "../resources/dataset/ensemble/"
    # with open(os.path.join(dir,"headers.txt"), "w+") as fw:
    #     for filename in os.listdir(dir):
    #         file = os.path.join(dir, filename)
    #         if os.path.isfile(file) and file.endswith(".csv"):
    #             fw.write("{}:\t{}".format(filename, open(file, "r").readline()))

    with open(os.path.join(dir, "headers.txt")) as f:
        dataset_str = f.read()
        print(dataset_str[:419])


    json_str, success = vars_dataset_connection(dkg_json_string, dataset_str, gpt_key)
    print(json_str)

    data_json = json.loads(json_str)

    # %%
    extraction = os.path.join(cache_dir, paper_name + "__mit-extraction.json")
    with open(extraction, 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    # %% md

    load_concise_vars(
        os.path.join(cache_dir, paper_name + "__mit-extraction.json"),
        os.path.join(cache_dir, paper_name + "__mit-concise.txt"))

    # generate json with dataset id in file "filename__mit-extraction_id.json"
    modify_dataset(
        os.path.join(cache_dir, paper_name + "__mit-extraction.json"),
        os.path.join(dir,'headers.txt'),
        os.path.join(dir,'catalog.txt'))

    # read and return json file from "filename__mit-extraction_id.json"
    with open(os.path.join(cache_dir, paper_name + "__mit-extraction_id.json"), 'r') as f:
        json_data = json.load(f)
    return json_data



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
    papers = load_paper_info("../../resources/xDD/xdd_paper.json")
    paper = papers[6]  # 0 1 4 6
    print(paper)

    mit_extraction(paper)
    mit_text = open('../../resources/xDD/mit-extraction/' + paper["title"] + '__mit-concise.txt',
                    "r").read()
    arizona_text = open('../../resources/xDD/arizona-extraction/variables_' + paper["title"] + '.txt',
                    "r").read()

    mit_arizona_map = build_map_from_concise_vars(mit_text, arizona_text)
    open('../../resources/xDD/mit-extraction/' + paper["title"] + '__map.txt', "w").write(mit_arizona_map)

    modify_dataset(
        '../../resources/xDD/mit-extraction/'+paper["title"]+'__mit-extraction.json',
        '../../resources/dataset/ensemble/headers.txt',
        '../../resources/dataset/ensemble/catalog.txt')
    # res = mit_extraction_restAPI("md5__d41d8cd98f00b204e9800998ecf8427e__1-s2.0-S2211379721005490-main.txt", gpt_key.GPT_KEY ,"/tmp/askem")
    # print(res)