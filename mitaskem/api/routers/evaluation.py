import os
import sys
import ast
from pathlib import Path

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from askem_extractions.data_model import *
from askem_extractions.importers import import_arizona, import_mit
from askem_extractions.importers.mit import merge_collections

from mitaskem.src.eval.data_quality import evaluate_variable_extraction, evaluate_model_card_extraction
from mitaskem.src.file_cache import save_file_to_cache
from mitaskem.src.mit_extraction import mit_extraction_restAPI, load_concise_vars, load_arizona_concise_vars, \
    build_map_from_concise_vars

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


router = APIRouter()

@router.post("/eval_var_extraction", tags=["Evaluation"])
async def eval_var_extraction(gpt_key: str, test_json_file: UploadFile = File(...), ground_truth_file: UploadFile = File(...)):
    """
        Upload MIT extractions from TA1 variable extraction module, and evaluate it with ground-truth file.
    """
    try:
        key = gpt_key
        cache_dir = "/tmp/askem"



        mit_contents = await test_json_file.read()
        # Assuming the file contains text, you can print it out
        print(mit_contents.decode())
        res_mit_file = save_file_to_cache(test_json_file.filename, mit_contents, cache_dir)
        mit_concise = res_mit_file.replace(".json","-concise.txt")
        print("file exist: ", os.path.isfile("/tmp/askem/"+res_mit_file))
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

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/eval_model_card", tags=["Evaluation"])
async def eval_model_card(gpt_key: str, test_json_file: UploadFile = File(...), ground_truth_file: UploadFile = File(...)):
    """
        Upload MIT model card output from TA1 mit service, and evaluate it with ground-truth file.
    """
    try:
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

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))