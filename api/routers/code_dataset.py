import os
import sys

from fastapi import APIRouter

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import code_dataset_connection

router = APIRouter()


@router.post("/run")
def run_code_text(input_code: str, input_dataset: str):

    return code_dataset_connection(code=input_code, dataset=input_dataset)
