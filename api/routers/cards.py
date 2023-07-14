import ast, io, random, sys, os
import asyncio
from typing import Optional

from pandas import read_csv
from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import construct_data_card, dataset_header_document_dkg, construct_model_card

router = APIRouter()

@router.post("/get_data_card", tags=["Data-and-model-cards"])

async def get_data_card(gpt_key: str, csv_file: UploadFile = File(...), doc_file: UploadFile = File(...), smart: Optional[bool] = False):
    """
           Smart run provides better results but may result in slow response times as a consequence of extra GPT calls.
    """
    files = [csv_file.read(), doc_file.read()]
    csv, doc = await asyncio.gather(*files)

    
    # TODO handle inputs that are too long to fit in the context window
    csv = csv.decode().strip()
    doc = doc.decode().strip()
    if len(csv) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Empty CSV file")
    if len(doc) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Empty document file")

    calls = [
        construct_data_card(data=csv, data_doc=doc, gpt_key=gpt_key),
        dataset_header_document_dkg(data=csv, doc=doc, gpt_key=gpt_key, smart=smart),
    ]

    results = await asyncio.gather(*calls)
    for s, success in results:
        if not success:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=s)

    data_card = ast.literal_eval(results[0][0])
    data_card['SCHEMA'] = [s.strip() for s in csv.split('\n')[0].split(',')]
    data_profiling = ast.literal_eval(results[1][0])
    if 'DATA_PROFILING_RESULT' in data_card:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='DATA_PROFILING_RESULT cannot be a requested field in the data card.')
    data_card['DATA_PROFILING_RESULT'] = data_profiling

    return data_card


@router.post("/get_model_card", tags=["Data-and-model-cards"])
async def get_model_card(gpt_key: str, text_file: UploadFile = File(...), code_file: UploadFile = File(...)):

    files = [text_file.read(), code_file.read()]
    text, code = await asyncio.gather(*files)

    # process model text
    text_string = text.decode()

    # process code
    code_string = code.decode()

    res, success = await construct_model_card(text=text_string, code=code_string, gpt_key=gpt_key)
    if not success:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=res)
    model_card = ast.literal_eval(res)
    return model_card
