import ast, io, random, sys, os, csv

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from mitaskem.src.file_cache import save_file_to_cache
from mitaskem.src.mit_extraction import async_mit_extraction_restAPI, afind_vars_from_text
from typing import Dict, Optional

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from mitaskem.src.text_search import text_var_search, vars_to_json, vars_dedup
from mitaskem.src.connect import vars_formula_connection, dataset_header_document_dkg, vars_dataset_connection_simplified, profile_matrix, get_dataset_type, process_data
from mitaskem.src.link_annos_to_pyacset import link_annos_to_pyacset
from mitaskem.src.response_types import TabularProfile, MatrixProfile

router = APIRouter()

from mitaskem.src.response_types import KGDomain

@router.post("/find_text_vars", tags=["Paper-2-annotated-vars"])
async def find_variables_from_text(gpt_key: str, file: UploadFile = File(...), kg_domain : KGDomain = 'epi') -> JSONResponse:

    contents = await file.read()
    json_str = await afind_vars_from_text(contents.decode(), gpt_key)
    return json_str

@router.post("/link_datasets_to_vars", tags=["Paper-2-annotated-vars"])
def link_dataset_columns_to_extracted_variables(json_str: str, dataset_str: str, gpt_key: str) -> JSONResponse:
    s, success = vars_dataset_connection_simplified(json_str=json_str, dataset_str=dataset_str, gpt_key=gpt_key)
    
    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_latex_to_vars", tags=["Paper-2-annotated-vars"])
def link_latex_formulas_to_extracted_variables(json_str: str, formula: str, gpt_key: str) -> JSONResponse:
    s, success = vars_formula_connection(json_str=json_str, formula=formula, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_annos_to_pyacset", tags=["Paper-2-annotated-vars"])
def link_annotation_to_pyacset_and_paper_info(pyacset_str: str, annotations_str: str, info_str: str = "") -> JSONResponse:
    s = link_annos_to_pyacset(pyacset_s = pyacset_str, annos_s = annotations_str, info_s = info_str)

    return ast.literal_eval(s)


@router.post("/profile_matrix_data", tags=["Paper-2-annotated-vars"], response_model=MatrixProfile)
async def profile_matrix_data(gpt_key: str, csv_file: UploadFile = File(...), doc_file: UploadFile = File(...)) -> JSONResponse:

    csv_string = await csv_file.read()
    csv_str = csv_string.decode()
    csv_reader = csv.reader(io.StringIO(csv_str), dialect=csv.Sniffer().sniff(csv_str.splitlines()[-1]))

    doc = await doc_file.read()
    doc = doc.decode()

    header = next(csv_reader)
    dataset_type = get_dataset_type(header)
    if dataset_type != 'matrix':
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid CSV file; data type does not seem to be a matrix.")
    data = header.extend(csv_reader)  # make sure header is included in data
    data = process_data(data)

    s, success = await profile_matrix(data=data, doc=doc, dataset_name=csv_file.filename, doc_name=doc_file.filename, gpt_key=gpt_key, smart=smart)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_dataset_col_to_dkg", tags=["Paper-2-annotated-vars"], response_model=Dict[str, TabularProfile])
async def link_dataset_columns_to_dkg_info(gpt_key: str, csv_file: UploadFile = File(...),
                                           doc_file: UploadFile = File(...), smart: Optional[bool] = False, kg_domain : KGDomain = KGDomain.epi) -> JSONResponse:
    """
           Smart run provides better results but may result in slow response times as a consequence of extra GPT calls.
    """
    csv_string = await csv_file.read()
    csv_str = csv_string.decode()
    csv_reader = csv.reader(io.StringIO(csv_str), dialect=csv.Sniffer().sniff(csv_str.splitlines()[-1]))

    doc = await doc_file.read()
    doc = doc.decode()

    header = next(csv_reader)
    dataset_type = get_dataset_type(header)
    if dataset_type == 'matrix':
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid CSV file; seems to be a matrix, not tabular.")
    elif dataset_type == 'no-header':
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid CSV file; no header found.")

    data = [header]
    data.extend(csv_reader)  # make sure header is included in data
    data = process_data(data)
    s, success = await dataset_header_document_dkg(data=data, doc=doc, dataset_name=csv_file.filename, doc_name=doc_file.filename, gpt_key=gpt_key, kg_domain=kg_domain.value, smart=smart)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

# @router.post("/link_dataset_col_to_dkg", tags=["Paper-2-annotated-vars"])
# def link_dataset_columns_to_dkg_info(csv_str: str, gpt_key: str) -> JSONResponse:
#     s, success = dataset_header_dkg(header=csv_str, gpt_key=gpt_key)
#
#     if not success:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)
#
#     return ast.literal_eval(s)

@router.post("/upload_file_extract/", tags=["Paper-2-annotated-vars"])
async def upload_file_annotate(gpt_key: str, file: UploadFile = File(...), 
                               kg_domain : KGDomain = KGDomain.epi) -> JSONResponse:
    """
        User Warning: Calling APIs may result in slow response times as a consequence of GPT-4.
    """
    contents = await file.read()
    key = gpt_key
    # Assuming the file contains text, you can print it out
    print(contents.decode())
    res_file = save_file_to_cache(file.filename, contents, "/tmp/askem")
    print("file exist: ", os.path.isfile("/tmp/askem/"+res_file))
    return await async_mit_extraction_restAPI(res_file, key, "/tmp/askem", kg_domain.value)