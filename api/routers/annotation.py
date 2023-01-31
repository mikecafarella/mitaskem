import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.gen_petri import *

router = APIRouter()

# WIP WIP WIP WIP

@router.post("/text_column", tags=["Petri net"])
def run_match_place_and_text_to_columns(text: str, place: str, columns: str, gpt_key: str):
    s, success = match_place_and_text_to_columns(text=text, place=place, columns=columns, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s