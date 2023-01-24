import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import code_formula_connection

router = APIRouter()


@router.post("/run")
def run_code_text(input_code: str, input_formula: str, gpt_key: str):

    s, success = code_formula_connection(code=input_code, formula=input_formula, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s
