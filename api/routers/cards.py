import ast, io, random, sys, os

from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import JSONResponse

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.connect import construct_data_card

router = APIRouter()

@router.post("/get_data_card", tags=["Data-and-model-cards"])
async def get_data_card(gpt_key: str, csv_file: UploadFile = File(...), doc_file: UploadFile = File(...)):

    csv_string = await csv_file.read()
    csv_string = csv_string.decode()
    csv_strings = csv_string.split('\n')

    if len(csv_strings) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Empty CSV file")

    # get header and <=5 random rows
    num_rows_to_sample = min(5, len(csv_strings) - 1)
    csv_str = csv_strings[0] + '\n' + '\n'.join(random.sample(csv_strings[1:], num_rows_to_sample))

    doc = await doc_file.read()
    doc = doc.decode()

    s, success = construct_data_card(data=csv_str, data_doc=doc, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=s)

    return ast.literal_eval(s)