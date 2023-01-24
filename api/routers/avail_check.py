import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import code_dataset_connection


router = APIRouter()


@router.post("/run")
def run_avail_check(input: str):
    return f"You sent us {input}"
