import ast, io, random, sys, os
import asyncio

from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import construct_data_card, dataset_header_document_dkg

router = APIRouter()

@router.post("/get_data_card", tags=["Data-and-model-cards"])
async def get_data_card(gpt_key: str, csv_file: UploadFile = File(...), doc_file: UploadFile = File(...)):

    files = [csv_file.read(), doc_file.read()]
    csv, doc = await asyncio.gather(*files)

    # process CSV; get header and <= 5 random rows
    csv_string = csv.decode()
    csv_strings = csv_string.split('\n')
    if len(csv_strings) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Empty CSV file")
    num_rows_to_sample = min(5, len(csv_strings) - 1)
    csv_str = csv_strings[0] + '\n' + '\n'.join(random.sample(csv_strings[1:], num_rows_to_sample))

    # process doc
    # TODO: handle docs that are too long to fit in the context window
    doc = doc.decode()

    calls = [construct_data_card(data=csv_str, data_doc=doc, gpt_key=gpt_key), dataset_header_document_dkg(header=csv_str, doc=doc, gpt_key=gpt_key)]
    results = await asyncio.gather(*calls)
    for s, success in results:
        if not success:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=s)

    data_card = ast.literal_eval(results[0][0])
    data_profiling = ast.literal_eval(results[1][0])
    if 'DATA_PROFILING_RESULT' in data_card:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='DATA_PROFILING_RESULT cannot be a requested field in the data card.')
    data_card['DATA_PROFILING_RESULT'] = data_profiling

    return data_card