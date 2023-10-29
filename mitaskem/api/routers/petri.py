import os
import sys
import ast

from fastapi import APIRouter,status
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from mitaskem.src.gen_petri import *
from mitaskem.src.pyacset_gen.convert_to_pyacset import *

router = APIRouter()


@router.post("/get_places", tags=["Code-2-Petri-net"])
def get_petri_net_places(code: str, gpt_key: str):
    s, success = get_places(text=code, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

@router.post("/get_transitions", tags=["Code-2-Petri-net"])
def get_petri_net_transitions(code: str, gpt_key: str):
    s, success = get_transitions(text=code, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

@router.post("/get_arcs", tags=["Code-2-Petri-net"])
def get_petri_net_arcs(code: str, gpt_key: str):
    s, success = get_arcs(text=code, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

@router.post("/get_pyacset", tags=["Code-2-Petri-net"])
def get_pyacset_from_components(places_str:str, transitions_str: str, arcs_str: str):
    s = convert_to_pyacset(places_s = places_str, transitions_s = transitions_str, arcs_s = arcs_str)

    return ast.literal_eval(s)

#@router.post("/match_place_to_text", tags=["Code-2-Petri-net"])
def run_match_place_to_text(text: str, place: str, gpt_key: str):
    s, success = match_place_to_text(text=text, place=place, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

#@router.post("/init_param_from_text", tags=["Code-2-Petri-net"])
def run_init_param_from_text(text: str, param: str, gpt_key: str):
    s, success = init_param_from_text(text=text, param=param, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s

#@router.post("/match_place_and_text_to_columns", tags=["Code-2-Petri-net"])
def run_match_place_and_text_to_columns(text: str, place: str, columns: str, gpt_key: str):
    s, success = match_place_and_text_to_columns(text=text, place=place, columns=columns, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return s