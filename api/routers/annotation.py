import ast, io, random, sys, os

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from file_cache import save_file_to_cache
from mit_extraction import async_mit_extraction_restAPI, afind_vars_from_text
from typing import Optional

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from src.text_search import text_var_search, vars_to_json, vars_dedup
from src.connect import vars_formula_connection, dataset_header_document_dkg, vars_dataset_connection_simplified, profile_matrix, get_dataset_type
from src.link_annos_to_pyacset import link_annos_to_pyacset

router = APIRouter()


@router.post("/find_text_vars", tags=["Paper-2-annotated-vars"])
async def find_variables_from_text(gpt_key: str, file: UploadFile = File(...)):

    contents = await file.read()
    json_str = await afind_vars_from_text(contents.decode(), gpt_key)
    return json_str

    length = len(text)
    segments = int(length/1000 + 1)

    outputs = ""

    for i in range(segments):
        snippet = text[i * 1000: (i+1) * 1000]
        s, success = text_var_search(text=snippet, gpt_key=gpt_key)

        if not success:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)
        
        outputs += s

    return ast.literal_eval(vars_to_json(vars_dedup(outputs)))

@router.post("/link_datasets_to_vars", tags=["Paper-2-annotated-vars"])
def link_dataset_columns_to_extracted_variables(json_str: str, dataset_str: str, gpt_key: str):
    s, success = vars_dataset_connection_simplified(json_str=json_str, dataset_str=dataset_str, gpt_key=gpt_key)
    
    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_latex_to_vars", tags=["Paper-2-annotated-vars"])
def link_latex_formulas_to_extracted_variables(json_str: str, formula: str, gpt_key: str):
    s, success = vars_formula_connection(json_str=json_str, formula=formula, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_annos_to_pyacset", tags=["Paper-2-annotated-vars"])
def link_annotation_to_pyacset_and_paper_info(pyacset_str: str, annotations_str: str, info_str: str = ""):
    s = link_annos_to_pyacset(pyacset_s = pyacset_str, annos_s = annotations_str, info_s = info_str)

    return ast.literal_eval(s)


@router.post("/profile_matrix_data", tags=["Paper-2-annotated-vars"])
async def profile_matrix_data(gpt_key: str, csv_file: UploadFile = File(...), doc_file: UploadFile = File(...)):
    csv_string = await csv_file.read()
    csv_str = csv_string.decode()

    doc = await doc_file.read()
    doc = doc.decode()

    dataset_type = get_dataset_type(csv_str)
    if dataset_type != 'matrix':
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid CSV file; data type does not seem to be a matrix.")

    s, success = await profile_matrix(data=csv_str, doc=doc, dataset_name=csv_file.filename, doc_name=doc_file.filename, gpt_key=gpt_key, smart=smart)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_dataset_col_to_dkg", tags=["Paper-2-annotated-vars"])
async def link_dataset_columns_to_dkg_info(gpt_key: str, csv_file: UploadFile = File(...),
                                           doc_file: UploadFile = File(...), smart: Optional[bool] = False):
    """
           Smart run provides better results but may result in slow response times as a consequence of extra GPT calls.
    """
    csv_string = await csv_file.read()
    csv_str = csv_string.decode()

    doc = await doc_file.read()
    doc = doc.decode()

    dataset_type = get_dataset_type(csv_str)
    if dataset_type == 'matrix':
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid CSV file; seems to be a matrix, not tabular.")

    s, success = await dataset_header_document_dkg(data=csv_str, doc=doc, dataset_name=csv_file.filename, doc_name=doc_file.filename, gpt_key=gpt_key, smart=smart)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

# @router.post("/link_dataset_col_to_dkg", tags=["Paper-2-annotated-vars"])
# def link_dataset_columns_to_dkg_info(csv_str: str, gpt_key: str):
#     s, success = dataset_header_dkg(header=csv_str, gpt_key=gpt_key)
#
#     if not success:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)
#
#     return ast.literal_eval(s)


@router.post("/upload_file_extract/", tags=["Paper-2-annotated-vars"])
async def upload_file_annotate(gpt_key: str, file: UploadFile = File(...)):
    """
        User Warning: Calling APIs may result in slow response times as a consequence of GPT-4.
    """
    try:
        contents = await file.read()
        key = gpt_key
        # Assuming the file contains text, you can print it out
        print(contents.decode())
        res_file = save_file_to_cache(file.filename, contents, "/tmp/askem")
        print("file exist: ", os.path.isfile("/tmp/askem/"+res_file))
        return await async_mit_extraction_restAPI(res_file, key, "/tmp/askem")

        # return {"file name": res_file, "file contents": text}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))