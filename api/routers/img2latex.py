import os
import sys

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.img_latex import img2latex

router = APIRouter()


@router.post("/convert", tags=["Image-to-LateX"])
def run_convert(img_local_path: str):

    s, success = img2latex(url="http://100.26.10.46:8502/bytes/", file=img_local_path)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s