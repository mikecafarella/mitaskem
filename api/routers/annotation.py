import os
import sys
import ast

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.text_search import text_var_search, vars_to_json, vars_dedup
from src.connect import vars_formula_connection
from src.link_annos_to_pyacset import link_annos_to_pyacset

router = APIRouter()


@router.post("/find_text_vars", tags=["Paper-2-annotated-vars"])
def find_variables_from_text(text: str, gpt_key: str):

    length = len(text)
    segments = int(length/1000 + 1)

    outputs = ""

    for i in range(segments):
        snippet = text[i * 1000: (i+1) * 1000]
        s, success = text_var_search(text=snippet, gpt_key=gpt_key)

        if not success:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)
        
        outputs += s

    return ast.literal_eval(vars_to_json(vars_dedup(outputs)))

@router.post("/link_latex_to_vars", tags=["Paper-2-annotated-vars"])
def link_latex_formulas_to_extracted_variables(json_str: str, formula: str, gpt_key: str):
    s, success = vars_formula_connection(json_str=json_str, formula=formula, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_annos_to_pyacset", tags=["Paper-2-annotated-vars"])
def link_annotation_to_pyacset_and_paper_info(pyacset_str: str, annotations_str: str, info_str: str = ""):
    s = link_annos_to_pyacset(pyacset_s = pyacset_str, annos_s = annotations_str, info_s = info_str)

    return s