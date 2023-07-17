import ast, io, random, sys, os
import asyncio
from typing import Optional

from openai import OpenAIError
from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import construct_data_card, dataset_header_document_dkg, construct_model_card, matrix_dkg, get_dataset_type

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

    data_type = get_dataset_type(csv)
    if data_type == 'header-0':
        schema = csv.split('\n')[0].strip()
        profiler = dataset_header_document_dkg
    elif data_type == 'no-header':
        schema = None
        profiler = dataset_header_document_dkg
    elif data_type == 'matrix':
        schema = None
        profiler = matrix_dkg
    else:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid CSV file; could not determine data type")

    calls = [
        construct_data_card(data_doc=doc, dataset_name=csv_file.filename, doc_name=doc_file.filename, dataset_type=data_type, gpt_key=gpt_key),
        profiler(data=csv, doc=doc, dataset_name=csv_file.filename, doc_name=doc_file.filename, gpt_key=gpt_key, smart=smart)
    ]

    try:
        results = await asyncio.gather(*calls)
    except OpenAIError as err:
        if "maximum context" in str(err):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Input too long. Please reduce the size of your input.")
        else:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"OpenAI connection error: {err}")

    for s, success in results:
        if not success:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=s)

    data_card = ast.literal_eval(results[0][0])
    data_profiling = ast.literal_eval(results[1][0])
    if 'DATA_PROFILING_RESULT' in data_card:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='DATA_PROFILING_RESULT cannot be a requested field in the data card.')

    if data_type == 'header-0':
        data_card['SCHEMA'] = [s.strip() for s in schema.split(',')]
        # get a random sample of a row from the csv
        data_card['EXAMPLES'] = {k.strip(): v for k, v in zip(schema.split(','), random.sample(csv.split('\n')[1:], 1)[0].split(','))}
        data_card['DATA_PROFILING_RESULT'] = data_profiling
        data_card['EXAMPLES'] = {k.strip(): v for k, v in zip(schema.split(','), random.sample(csv.split('\n')[1:], 1)[0].split(','))}
    elif data_type == 'no-header':
        if 'SCHEMA' not in data_card:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='SCHEMA not found in data card')
        schema = [s.strip() for s in data_card['SCHEMA'].split(',')]
        schema = [s[1:] if s.startswith('[') else s for s in schema]
        schema = [s[:-1] if s.endswith(']') else s for s in schema]
        aligned_data_profiling = {}
        for k, v in data_profiling.items():
            k = int(k)
            k = schema[k]
            aligned_data_profiling[k] = v
        data_card['DATA_PROFILING_RESULT'] = aligned_data_profiling
        data_card['EXAMPLES'] = {k.strip(): v for k, v in zip(schema.split(','), random.sample(csv.split('\n')[1:], 1)[0].split(','))}
    elif data_type == 'matrix':
        data_card['DATA_PROFILING_RESULT'] = data_profiling
        data_card['EXAMPLES'] = random.sample(csv.split('\n'), 1)[0].split(',')
    else:
        raise Exception('Invalid data type')


    return data_card


@router.post("/get_model_card", tags=["Data-and-model-cards"])
async def get_model_card(gpt_key: str, text_file: UploadFile = File(...), code_file: UploadFile = File(...)):

    files = [text_file.read(), code_file.read()]
    text, code = await asyncio.gather(*files)

    # process model text
    text_string = text.decode()

    # process code
    code_string = code.decode()

    try:
        res, success = await construct_model_card(text=text_string, code=code_string, gpt_key=gpt_key)
    except OpenAIError as err:
        if "maximum context" in str(err):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Input too long. Please reduce the size of your input.")
        else:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"OpenAI connection error: {err}")

    if not success:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=res)
    model_card = ast.literal_eval(res)
    return model_card
