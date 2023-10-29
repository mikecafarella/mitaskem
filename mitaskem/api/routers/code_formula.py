import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from mitaskem.src.connect import code_formula_connection

router = APIRouter()


@router.post("/run", tags=["Code-to-format"])
def run_code_formula(input_code: str, input_formulas: str, gpt_key: str):

    s, success = code_formula_connection(code=input_code, formulas=input_formulas, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s
