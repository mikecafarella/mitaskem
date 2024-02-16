import os
import sys
import ast
from pathlib import Path

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from askem_extractions.data_model import *
from askem_extractions.importers import import_arizona, import_mit
from askem_extractions.importers.mit import merge_collections

from mitaskem.src.eval.data_quality import evaluate_variable_extraction, evaluate_model_card_extraction, \
    count_variable_extraction, get_var_cleaning_extraction, evaluate_variable_grd_extraction
from mitaskem.src.eval.load_concise import extract_text_by_color
from mitaskem.src.file_cache import save_file_to_cache
from mitaskem.src.mit_extraction import mit_extraction_restAPI, load_concise_vars, load_arizona_concise_vars, \
    build_map_from_concise_vars
from mitaskem.src.response_types import VarEval

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

router = APIRouter()


@router.post("/eval_var_extraction", tags=["Evaluation"])
async def eval_var_extraction(gpt_key: str, test_json_file: UploadFile = File(...),
                              ground_truth_file: UploadFile = File(...)):
    """
        Upload MIT extractions from TA1 variable extraction module, and evaluate it with ground-truth file.
    """
    key = gpt_key
    cache_dir = "/tmp/askem"
    mit_contents = await test_json_file.read()
    # Assuming the file contains text, you can print it out
    print(mit_contents.decode())
    res_mit_file = save_file_to_cache(test_json_file.filename, mit_contents, cache_dir)
    mit_concise = res_mit_file.replace(".json", "-concise.txt")
    print("file exist: ", os.path.isfile("/tmp/askem/" + res_mit_file))
    load_concise_vars(
        os.path.join(cache_dir, res_mit_file),
        os.path.join(cache_dir, mit_concise))

    mit_text = open(os.path.join(cache_dir, mit_concise)).read()
    print(mit_text)

    grd_truth_contents = await ground_truth_file.read()
    # Assuming the file contains text, you can print it out
    grd_truth_text = grd_truth_contents.decode()
    print(grd_truth_text)
    print("sending to gpt for eval")

    prec_recall = evaluate_variable_extraction(mit_text, grd_truth_text, key)
    # split by comma
    prec_re = prec_recall.split("\n")[0].split(",")
    return {"precision": prec_re[0], "recall": prec_re[1]}


@router.post("/eval_var_extraction_benchmark", tags=["Evaluation"], response_model=VarEval)
async def eval_var_extraction_with_benchmark(gpt_key: str, test_json_file: UploadFile = File(...),
                                             ground_truth_json_file: UploadFile = File(...)):
    """
        Evaluate MIT extractions from TA1 variable extraction module with annotated ground-truth json file.
    """
    key = gpt_key
    cache_dir = "/tmp/askem"
    mit_contents = await test_json_file.read()
    # Assuming the file contains text, you can print it out
    print(mit_contents.decode())
    res_mit_file = save_file_to_cache(test_json_file.filename, mit_contents, cache_dir)
    if res_mit_file.endswith(".json"):
        mit_concise = res_mit_file.replace(".json", "-concise.txt")
    else:
        mit_concise = res_mit_file + "-concise.txt"
    print("file exist: ", os.path.isfile(cache_dir + "/" + res_mit_file))
    load_concise_vars(
        os.path.join(cache_dir, res_mit_file),
        os.path.join(cache_dir, mit_concise))

    mit_text = open(os.path.join(cache_dir, mit_concise)).read()
    print(mit_text)
    count_tool_gpt = count_variable_extraction(mit_text)

    grd_truth_contents = await ground_truth_json_file.read()
    # Assuming the file contains text, you can print it out
    grd_truth_text = grd_truth_contents.decode()
    print(grd_truth_text)
    gd_json_file = save_file_to_cache(ground_truth_json_file.filename, grd_truth_contents, cache_dir)
    print("sending to gpt for eval")

    if gd_json_file.endswith(".json"):
        grd_var = gd_json_file.replace(".json", "-concise.txt")
    else:
        grd_var = gd_json_file + "-concise.txt"
    extract_text_by_color(os.path.join(cache_dir, gd_json_file),
                          os.path.join(cache_dir, grd_var), "#ffd100")
    grd_text = open(os.path.join(cache_dir, grd_var)).read()
    print(grd_text)

    count_grd = count_variable_extraction(grd_text)
    print("number of variable in ground truth: ", count_grd)

    grd_clean = get_var_cleaning_extraction(grd_text, key)
    print(grd_clean)
    count_grd_clean = count_variable_extraction(grd_clean)
    print("number of variable in test json file: ", count_tool_gpt)
    print("number of variable in cleaned ground truth: ", count_grd_clean)

    tool_match = evaluate_variable_grd_extraction(mit_text, grd_clean, key)
    print(tool_match)
    count_tool_match = count_variable_extraction(tool_match)
    tool_precision = count_tool_match / count_tool_gpt
    tool_recall = count_tool_match / count_grd_clean
    # sometimes the number of variable in tool match is larger than the number of variable in ground truth becaues of the decomposition of variable combination
    if tool_precision > 1.0:
        tool_precision = 1.0
    if tool_recall > 1.0:
        tool_recall = 1.0
    print("number of variable in tool match: ", count_tool_match)
    return {"PRECISION": tool_precision, "RECALL": tool_recall,
            "F1_SCORE": 2 * tool_precision * tool_recall / (tool_precision + tool_recall)}


@router.post("/eval_model_card", tags=["Evaluation"])
async def eval_model_card(gpt_key: str, test_json_file: UploadFile = File(...),
                          ground_truth_file: UploadFile = File(...)):
    """
        Upload MIT model card output from TA1 mit service, and evaluate it with ground-truth file.
    """
    key = gpt_key
    mit_contents = await test_json_file.read()
    mit_text = mit_contents.decode()
    print(mit_text)

    grd_truth_contents = await ground_truth_file.read()
    grd_truth_text = grd_truth_contents.decode()
    print(grd_truth_text)
    print("sending to gpt for eval")

    prec_recall = evaluate_model_card_extraction(mit_text, grd_truth_text, key)
    acc = prec_recall.split("\n")[0]
    return {"accuracy": acc}
