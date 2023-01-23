import os
import sys

from fastapi import APIRouter

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import code_text_connection

router = APIRouter()


@router.post("/run")
def run_code_text(input_code: str, input_text: str):

    return code_text_connection(code=input_code, text=input_text)
