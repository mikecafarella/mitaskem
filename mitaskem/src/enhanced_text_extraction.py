import ast
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

import requests
from askem_extractions.importers import import_mit

from mitaskem.src.connect import vars_dataset_connection_simplified
from mitaskem.src.dataset_id import modify_dataset
from mitaskem.src.eval.data_quality import get_var_whole_tool_extraction, post_pdf_to_api, extract_content_to_txt, \
    get_var_whole_extraction, count_variable_extraction, get_var_cleaning_extraction, evaluate_variable_grd_extraction, \
    get_var_extract_tool_extraction, get_deduplicate_extraction
from mitaskem.src.eval.load_concise import extract_text_by_color
from mitaskem.src.mit_extraction import load_arizona_concise_vars, load_concise_vars_from_raw
from mitaskem.src.text_search import avars_to_json, vars_dedup
from mitaskem.src.xdd.xdd_client import get_text_from_pdf

GPT_KEY = os.environ.get('OPENAI_API_KEY')

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
    md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
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


def process_papers(cache_dir = "/tmp/askem"):
    # Specify the directory you want to search
    directory = "/Users/chunwei/Downloads/third pass/jsons/"

    # Get a list of all files in the directory with a .json extension
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    # json_files = ["11-16-PAG-annotated-context-annotations-bertozzi-et-al-2020-the-challenges-of-modeling-and-forecasting-the-spread-of-covid-19.json"]

    # Create a csv file to store the results
    csv_file = open('acc_results.csv', 'w')

    # Iterate over each json file
    # add execption handling for each loop

    for json_file in json_files:
        file_name = json_file.replace(".json", "")
        print("Working on ", file_name)

        # start to process the file
        paper_name = file_name
        pdf_path = f'/Users/chunwei/Downloads/third pass/paper/{paper_name}.pdf'

        with open(pdf_path, "rb") as file:
            bytes = file.read()
            text = get_text_from_pdf(pdf_path, bytes, enable_file_cache = True, cache_dir = cache_dir)

        paper_text_file = f'/Users/chunwei/Downloads/third pass/text/{paper_name}.txt'
        with open(paper_text_file, "w") as text_file:
            text_file.write(text)

        pure_gpt = get_var_whole_extraction(text, GPT_KEY)
        print("pure gpt extraction output:")
        print(pure_gpt)

        # count how many variables are extracted
        pure_count = count_variable_extraction(pure_gpt)
        print("number of variable in mit extraction: ", pure_count)
        print()

        # evaluate the whole text extraction with Arizona tool
        skema_res = get_skema_var_extraction(text)
        json_str = skema_res
        # print(json_str)

        tool_response_json = json.loads(json_str)
        # create a dummy json file for tool extraction
        tool_json_file = '/tmp/mit-skema.json'
        with open(tool_json_file, 'w') as outfile:
            json.dump(tool_response_json, outfile)
        tool_concise = tool_json_file.replace(".json", "-concise.txt")

        load_arizona_concise_vars(tool_json_file, tool_concise)
        tool_text = open(tool_concise).read()
        # print(tool_text)

        count_tool = count_variable_extraction(tool_text)
        print("number of variable in Arizona tool extraction: ", count_tool)

        # test the whole text extraction with Arizona tool
        tool_gpt = get_var_whole_tool_extraction(text, tool_text, GPT_KEY)
        print("tool gpt extraction output:")
        print(tool_gpt)
        count_tool_gpt = count_variable_extraction(tool_gpt)
        print("number of variable in GPT-tool extraction: ", count_tool_gpt)

        # test the merged extraction with Arizona tool and pure gpt extraction
        merged_gpt = get_var_extract_tool_extraction(pure_gpt, tool_text, GPT_KEY)
        print("merged gpt extraction output:")
        print(merged_gpt)
        count_merged = count_variable_extraction(merged_gpt)
        print("number of variable in merged extraction: ", count_merged)


        # get the ground truth
        ground_truth = f'/Users/chunwei/Downloads/third pass/jsons/{paper_name}.json'
        grd_text = ground_truth.replace(".json", "-concise.txt")
        extract_text_by_color(ground_truth, grd_text, "#ffd100")
        grd_text = open(grd_text).read()
        print()
        print("ground truth entires: ")
        print(grd_text)

        count_grd = count_variable_extraction(grd_text)
        print("number of variable in ground truth: ", count_grd)
        print()

        grd_clean = get_var_cleaning_extraction(grd_text, GPT_KEY)
        print("cleaned ground truth: ")
        print(grd_clean)
        count_grd_clean = count_variable_extraction(grd_clean)
        print("number of variable in cleaned ground truth: ", count_grd_clean)
        print()

        # Evaluate the SKEMA extraction with clean ground truth
        dedup = get_deduplicate_extraction(tool_text, GPT_KEY)
        print("SKEMA extraction after deduplication: ")
        print(dedup)
        skema_match = evaluate_variable_grd_extraction(dedup, grd_clean, GPT_KEY)
        print("skema match: ")
        print(skema_match)
        count_skema_match = count_variable_extraction(skema_match)
        skema_precision = count_skema_match / count_tool
        skema_recall = count_skema_match / count_grd_clean
        if skema_recall>1:
            skema_recall = 1
        print("number of variable in skema match: ", count_skema_match)
        print("precision: ", skema_precision)
        print("recall: ", skema_recall)
        print()

        # Evaluate the MIT extraction with clean ground truth
        pure_match = evaluate_variable_grd_extraction(pure_gpt, grd_clean, GPT_KEY)
        print("pure match: ")
        print(pure_match)
        count_pure_match = count_variable_extraction(pure_match)
        pure_precision = count_pure_match / pure_count
        pure_recall = count_pure_match / count_grd_clean
        if pure_recall>1:
            pure_recall = 1
        print("number of variable in pure match: ", count_pure_match)
        print("precision: ", pure_precision)
        print("recall: ", pure_recall)
        print()

        # Evaluate the MIT tool extraction with clean ground truth
        tool_match = evaluate_variable_grd_extraction(tool_gpt, grd_clean, GPT_KEY)
        print("tool match: ")
        print(tool_match)
        count_tool_match = count_variable_extraction(tool_match)
        tool_precision = count_tool_match / count_tool_gpt
        tool_recall = count_tool_match / count_grd_clean
        if tool_recall>1:
            tool_recall = 1
        print("number of variable in tool match: ", count_tool_match)
        print("precision: ", tool_precision)
        print("recall: ", tool_recall)

        # Evaluate the merged extraction with clean ground truth
        merged_match = evaluate_variable_grd_extraction(merged_gpt, grd_clean, GPT_KEY)
        print("merged match: ")
        print(merged_match)
        count_merged_match = count_variable_extraction(merged_match)
        merged_precision = count_merged_match / count_merged
        merged_recall = count_merged_match / count_grd_clean
        if merged_recall>1:
            merged_recall = 1
        print("number of variable in merged match: ", count_merged_match)
        print("precision: ", merged_precision)
        print("recall: ", merged_recall)

        # write the file name, count_grd, count_grd_clean, count_tool, pure_count, count_tool_gpt, skema_match, count_pure_match, count_tool_match, skema_precision, skema_recall, pure_precision, pure_recall, tool_precision, tool_recall
        csv_file.write(f"{file_name},{count_grd},{count_grd_clean},"
                       f"{count_tool},{pure_count},{count_tool_gpt}, {count_merged},"
                       f"{count_skema_match},{count_pure_match},{count_tool_match},{count_merged_match},"
                       f"{skema_precision},{skema_recall},{2*skema_precision*skema_recall/(skema_precision+skema_recall)},"
                       f"{pure_precision},{pure_recall},{2*pure_precision*pure_recall/(pure_precision+pure_recall)},"
                       f"{tool_precision},{tool_recall},{2*tool_precision*tool_recall/(tool_precision+tool_recall)},"
                       f"{merged_precision},{merged_recall},{2*merged_recall*merged_precision/(merged_precision+merged_recall)}\n")
        csv_file.flush()
        # except:
        #     print("Error: ", file_name)
        #     continue
    csv_file.close()



if __name__ == "__main__":
    temp_dir = tempfile.gettempdir()
    cosmos_file_cache_dir = os.path.join(temp_dir, "cosmos")
    # create the directory if it does not exist
    if not os.path.exists(cosmos_file_cache_dir):
        os.makedirs(cosmos_file_cache_dir)
    process_papers(cache_dir=cosmos_file_cache_dir)