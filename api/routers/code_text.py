import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import code_text_connection

router = APIRouter()


@router.post("/run")
def run_code_text(input_code: str, input_text: str):

    s, success = code_text_connection(code=input_code, text=input_text)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s