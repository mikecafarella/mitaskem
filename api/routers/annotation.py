import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.text_search import text_var_search, vars_to_json, vars_dedup
from src.connect import vars_formula_connection

router = APIRouter()


@router.post("/find_text_vars", tags=["Paper-2-annotated-vars"])
def find_variables_from_text(text: str, gpt_key: str):
    s, success = text_var_search(text=text, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return vars_to_json(vars_dedup(s))

@router.post("/link_latex_to_vars", tags=["Paper-2-annotated-vars"])
def link_latex_formulas_to_extracted_variables(json_str: str, formula: str, gpt_key: str):
    s, success = vars_formula_connection(json_str=json_str, formula=formula, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s