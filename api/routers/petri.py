import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.gen_petri import *

router = APIRouter()


@router.post("/get_places", tags=["Petri net"])
def run_places(code: str, gpt_key: str):
    s, success = get_places(text=code, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

@router.post("/get_parameters", tags=["Petri net"])
def run_places(code: str, gpt_key: str):
    s, success = get_parameters(text=code, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

@router.post("/get_transitions", tags=["Petri net"])
def run_transitions(code: str, gpt_key: str):
    s, success = run_transitions(text=code, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s