import ast
import hashlib
import json
import os
import time
from pathlib import Path

import requests
from askem_extractions.importers import import_mit

from mitaskem.src.connect import vars_dataset_connection_simplified
from mitaskem.src.dataset_id import modify_dataset
from mitaskem.src.eval.data_quality import get_var_whole_tool_extraction
from mitaskem.src.mit_extraction import load_arizona_concise_vars, load_concise_vars_from_raw
from mitaskem.src.text_search import avars_to_json, vars_dedup

def get_skema_var_extraction(file_text):
    url = 'https://api.askem.lum.ai/text-reading/integrated-text-extractions'
    params = {
        "annotate_skema": True,
        "annotate_mit": False

    }
    files = {"texts": [file_text]}

    resp = requests.post(url, params=params, json=files)
    return resp.text


async def find_vars_from_text_enhanced(text: str, api_key: str, kg_domain : str):

    skema_res = get_skema_var_extraction(text)
    # generate uuid based on text
    md5 = hashlib.md5(text).hexdigest()
    tool_response_json = json.loads(skema_res)
    tool_json_file = f'/tmp/{md5}-mit-skema-tmp.json'
    with open(tool_json_file, 'w') as outfile:
        json.dump(tool_response_json, outfile)
    tool_concise = tool_json_file.replace(".json", "-concise.txt")
    load_arizona_concise_vars(tool_json_file, tool_concise)
    tool_text = open(tool_concise).read()
    print(tool_text)

    start = time.time()
    res = get_var_whole_tool_extraction(text, tool_text, api_key)
    openai_done = time.time()
    print(res)
    tmp1 = vars_dedup(res)
    print('tmp1', tmp1)

    print(f'{openai_done - start = }')

    tmp2 = await avars_to_json(tmp1, kg_domain)
    mira_done = time.time()
    print(f'{mira_done - openai_done = }')
    return ast.literal_eval(tmp2)

#@profile

async def async_mit_extraction_enhanced_restAPI(file_name, gpt_key, cache_dir, kg_domain : str):
    start = time.time()
    paper_name = file_name.split(".txt")[0]
    org_file = os.path.join(cache_dir, file_name)
    print("is file existing", os.path.exists(org_file))

    file_path = org_file
    t2 = time.time()
    print(f'{t2 - start=}')
    with open(file_path, "r") as f:
        text = f.read()
        json_str = await find_vars_from_text_enhanced(text, gpt_key, kg_domain)
    # dkg_json = json.loads(json.dumps(json_str))
    print('after variable extraction', json_str)

    t3 = time.time()
    print(f'{t3- t2=}')
    dkg_json = json_str
    for variable in dkg_json:
        variable["title"] = paper_name
    dkg_json_string = json.dumps(dkg_json)

    # print(dkg_json_string)
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

    json_str, success = vars_dataset_connection_simplified(dkg_json_string, dataset_str, gpt_key)
    print('after dataset connection', json_str)
    t4 = time.time()
    print(f'{t4-t3=}')
    #  print(json_str)

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
        os.path.join(dir, 'headers.txt'),
        os.path.join(dir, 'catalog.txt'))

    # read and file from "filename__mit-extraction_id.json" and convert to TA1 json format
    a_collection = import_mit(Path(cache_dir) / (paper_name + "__mit-extraction_id.json"))
    return a_collection
