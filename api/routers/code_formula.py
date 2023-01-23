import os
import sys

from fastapi import APIRouter

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import code_formula_connection

router = APIRouter()


@router.post("/run")
def run_code_text(input_code: str, input_formula: str):

    return code_formula_connection(code=input_code, formula=input_formula)
