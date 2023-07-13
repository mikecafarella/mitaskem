
import ast, json, requests, os
from pathlib import Path

from askem_extractions.importers import import_mit

import gpt_key
from connect import get_mit_arizona_var_prompt, get_gpt4_match, vars_dataset_connection_simplified
from dataset_id import modify_dataset
from ensemble.ensemble import load_paper_info, extract_variables, extract_vars
from gpt_key import *
from text_search import text_var_search, vars_dedup, vars_to_json

PARAM = "/Users/chunwei/research/mitaskem/resources/xDD/params/"
API_ROOT = "http://0.0.0.0:8000/"

def load_concise_vars(input_file, o_file):
    # Read JSON data from the file
    with open(input_file, 'r') as file:
        json_data = json.load(file)

    # Open a new file to write the output
    with open(o_file, 'w') as output_file:
        # Extract id, name, and text_annotations for each variable
        for item in json_data['attributes']:
            if 'id' not in item['payload']:
                continue
            variable_id = item['payload']['id']['id']
            variable_name = item['payload']['names'][0]['name']
            value = item['payload']['descriptions'][0]['source']
            output_line = f"{variable_id}, {variable_name}: {value}\n"

            # Write the extracted information to the output file
            output_file.write(output_line)

def load_concise_vars_from_raw(input_file, o_file):
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

def load_arizona_concise_vars(input_file, o_file):
    # Read JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Extract relevant information
    output = []
    for item in data['attributes']:
        if 'id' not in item['payload'] or 'names' not in item['payload'] or 'descriptions' not in item['payload']:
            continue
        variable_id = item['payload']['id']['id']
        print(variable_id)
        variable_name = item['payload']['names'][0]['name']
        if len(item['payload']['descriptions']) == 0:
            value = ""
        else:
            value = item['payload']['descriptions'][0]['source']
        output.append(f"{variable_id}, {variable_name}: {value}\n")



    # Open a new file to write the output
    with open(o_file, 'w') as output_file:
        # Extract id, name, and text_annotations for each variable
        # Print the extracted output
        for line in output:
            # Write the extracted information to the output file
            output_file.write(line)

def load_arizona_concise_vars_from_raw(input_file, o_file):
    # Read JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Extract relevant information
    output = []
    for item in data:
        if 'arguments' not in item:
            continue
        variable_id = item['id']
        variable_name = item['arguments']['variable'][0]['text']
        value = item['text']
        output.append(f"{variable_id}, {variable_name}: {value}\n")



    # Open a new file to write the output
    with open(o_file, 'w') as output_file:
        # Extract id, name, and text_annotations for each variable
        # Print the extracted output
        for line in output:
            # Write the extracted information to the output file
            output_file.write(line)


def build_map_from_concise_vars(mit, arizona, gpt_key):
    def process_match(m):
        m = m.split("```")
        if len(m) > 1:
            m = m[1]
        else:
            m = m[0]
        m = m.split("\n")
        m = [x for x in m if ":" in x]
        m = "\n".join(m)
        return m

    print(">> MIT")
    print(mit)
    print(">> Arizona")
    print(arizona)
    prompt = get_mit_arizona_var_prompt(mit, arizona)
    ans = get_gpt4_match(prompt, gpt_key, model="gpt-4-0314")
    ans = process_match(ans)
    print(">> Processed match")
    print(ans)
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

from methods import create_prompt_tasks, fork_join_requests, split_latex_into_chunks

async def _extract_text_vars(text, var_prompt):
    model_name = 'text-davinci-003'
    document_chunks = split_latex_into_chunks(document=text, prompt_template=var_prompt, model_name=model_name, 
                                              max_total_size=None, max_answer_size=256, chunk_overlap=0)
    
    task_prompts = [var_prompt.replace('[TEXT]', doc_chunk) for doc_chunk in document_chunks]
    res = await fork_join_requests(task_prompts, model=model_name)

    fres = []
    for r in res:
        fres.append(r.strip('\nNone')) # always ends in \nNone with current prompt...

    unified = '\n'.join(fres)
    tmp1 = vars_dedup(unified)
    return tmp1

async def afind_vars_from_text(text: str, gpt_key: str):
    with open(os.path.join(os.path.dirname(__file__), 'prompts/text_var_prompt.txt'), "r") as f:
        var_prompt = f.read()
    
    res = await _extract_text_vars(text, var_prompt)
    
    tmp2 = vars_to_json(res)
    return ast.literal_eval(tmp2)

async def async_mit_extraction_restAPI(file_name, gpt_key, cache_dir="/tmp/askem"):
    paper_name = file_name.split(".txt")[0]
    org_file = os.path.join(cache_dir, file_name)
    print("is file existing", os.path.exists(org_file))
    extract_vars(org_file, cache_dir)
    file_path = os.path.join(cache_dir, paper_name+"_vars.txt")
    print(file_path)
    with open(file_path, "r") as f:
        text = f.read()
        json_str = await afind_vars_from_text(text, gpt_key)
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


    json_str, success = vars_dataset_connection_simplified(dkg_json_string, dataset_str, gpt_key)
    print(json_str)

    data_json = json.loads(json_str)

    # %%
    extraction = os.path.join(cache_dir, paper_name + "__mit-extraction.json")
    with open(extraction, 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    # %% md

    load_concise_vars_from_raw(
        os.path.join(cache_dir, paper_name + "__mit-extraction.json"),
        os.path.join(cache_dir, paper_name + "__mit-concise.txt"))

    # generate json with dataset id in file "filename__mit-extraction_id.json"
    modify_dataset(
        os.path.join(cache_dir, paper_name + "__mit-extraction.json"),
        os.path.join(dir,'headers.txt'),
        os.path.join(dir,'catalog.txt'))

    # read and file from "filename__mit-extraction_id.json" and convert to TA1 json format
    a_collection = import_mit(Path(cache_dir) / ( paper_name + "__mit-extraction_id.json"))
    return a_collection

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


    json_str, success = vars_dataset_connection_simplified(dkg_json_string, dataset_str, gpt_key)
    print(json_str)

    data_json = json.loads(json_str)

    # %%
    extraction = os.path.join(cache_dir, paper_name + "__mit-extraction.json")
    with open(extraction, 'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    # %% md

    load_concise_vars_from_raw(
        os.path.join(cache_dir, paper_name + "__mit-extraction.json"),
        os.path.join(cache_dir, paper_name + "__mit-concise.txt"))

    # generate json with dataset id in file "filename__mit-extraction_id.json"
    modify_dataset(
        os.path.join(cache_dir, paper_name + "__mit-extraction.json"),
        os.path.join(dir,'headers.txt'),
        os.path.join(dir,'catalog.txt'))

    # read and file from "filename__mit-extraction_id.json" and convert to TA1 json format
    a_collection = import_mit(Path(cache_dir) / ( paper_name + "__mit-extraction_id.json"))
    return a_collection

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

    json_str, success = vars_dataset_connection_simplified(dkg_json_string, dataset_str, GPT_KEY)
    print(json_str)

    data_json = json.loads(json_str)

    # %%
    with open(
            "/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/" + paper["title"] + '__mit-extraction.json',
            'w', encoding='utf-8') as json_file:
        json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    # %% md

    load_concise_vars_from_raw(
        "/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/" + paper["title"] + '__mit-extraction.json',
        "/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/" + paper["title"] + '__mit-concise.txt')

    # generate json with dataset id in file "filename__mit-extraction_id.json"
    modify_dataset(
        '/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction/' + paper["title"] + '__mit-extraction.json',
        '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/headers.txt',
        '/Users/chunwei/research/mitaskem/resources/dataset/ensemble/catalog.txt')

    a_collection = import_mit(Path('/Users/chunwei/research/mitaskem/resources/xDD/mit-extraction') / (paper["title"] + "__mit-extraction_id.json"))
    return a_collection


if __name__ == "__main__":
    papers = load_paper_info("../../resources/xDD/xdd_paper.json")
    paper = papers[0]  # 0 1 4 6
    print(paper)

    mit_extraction(paper)
    # mit_text = open('../../resources/xDD/mit-extraction/' + paper["title"] + '__mit-concise.txt',
    #                 "r").read()

    # arizona_text = open('../../resources/xDD/arizona-extraction/variables_' + paper["title"] + '.txt',
    #                 "r").read()
    #
    # mit_arizona_map = build_map_from_concise_vars(mit_text, arizona_text,gpt_key.GPT_KEY)
    # open('../../resources/xDD/mit-extraction/' + paper["title"] + '__map.txt', "w").write(mit_arizona_map)
    #
    # modify_dataset(
    #     '../../resources/xDD/mit-extraction/'+paper["title"]+'__mit-extraction.json',
    #     '../../resources/dataset/ensemble/headers.txt',
    #     '../../resources/dataset/ensemble/catalog.txt')
    # res = mit_extraction_restAPI("md5__d41d8cd98f00b204e9800998ecf8427e__1-s2.0-S2211379721005490-main.txt", gpt_key.GPT_KEY ,"/tmp/askem")
    # print(res)
    # res_mit_file = "/Users/chunwei/research/ASKEM-TA1-DataModel/examples/a_temp.json"
    # mit_concise = res_mit_file.replace(".json", "-concise.txt")
    # load_arizona_concise_vars(res_mit_file,mit_concise)
    # print(open(mit_concise,"r").read())