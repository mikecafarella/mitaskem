import ast, io, random, sys, os, csv

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from mitaskem.src.enhanced_text_extraction import async_mit_extraction_enhanced_restAPI
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
import logging


@router.post("/find_text_vars", tags=["Paper-2-annotated-vars"], deprecated=True)
async def find_variables_from_text(gpt_key: str, file: UploadFile = File(...), kg_domain : KGDomain = 'epi') -> JSONResponse:

    contents = await file.read()
    json_str = await afind_vars_from_text(contents.decode(), gpt_key)
    return json_str

@router.post("/link_datasets_to_vars", tags=["Paper-2-annotated-vars"], deprecated=True)
def link_dataset_columns_to_extracted_variables(json_str: str, dataset_str: str, gpt_key: str) -> JSONResponse:
    s, success = vars_dataset_connection_simplified(json_str=json_str, dataset_str=dataset_str, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_latex_to_vars", tags=["Paper-2-annotated-vars"], deprecated=True)
def link_latex_formulas_to_extracted_variables(json_str: str, formula: str, gpt_key: str) -> JSONResponse:
    s, success = vars_formula_connection(json_str=json_str, formula=formula, gpt_key=gpt_key)

    if not success:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=s)

    return ast.literal_eval(s)

@router.post("/link_annos_to_pyacset", tags=["Paper-2-annotated-vars"], deprecated=True)
def link_annotation_to_pyacset_and_paper_info(pyacset_str: str, annotations_str: str, info_str: str = "") -> JSONResponse:
    s = link_annos_to_pyacset(pyacset_s = pyacset_str, annos_s = annotations_str, info_s = info_str)

    return ast.literal_eval(s)


@router.post("/profile_matrix_data", tags=["Paper-2-annotated-vars"], response_model=MatrixProfile, deprecated=True)
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

@router.post("/link_dataset_col_to_dkg", tags=["Paper-2-annotated-vars"], response_model=Dict[str, TabularProfile], deprecated=True)
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

from askem_extractions.data_model import AttributeCollection

@router.post("/upload_file_extract/", tags=["Paper-2-annotated-vars"], response_model=AttributeCollection)
async def upload_file_annotate(gpt_key: str, file: UploadFile = File(...),
                               kg_domain : KGDomain = KGDomain.epi) -> JSONResponse:
    """
        User Warning: Calling APIs may result in slow response times as a consequence of GPT-4.
    """
    contents = await file.read()
    key = gpt_key
    # Assuming the file contains text, you can print it out
    logging.log(contents.decode())
    res_file = save_file_to_cache(file.filename, contents, "/tmp/askem")
    logging.log("file exist: ", os.path.isfile("/tmp/askem/"+res_file))
    return await async_mit_extraction_restAPI(res_file, key, "/tmp/askem", kg_domain.value)


@router.post("/upload_file_extract_enhanced/", tags=["Paper-2-annotated-vars"], response_model=AttributeCollection)
async def upload_file_annotate_enhanced(gpt_key: str, file: UploadFile = File(...),
                               kg_domain : KGDomain = KGDomain.epi) -> JSONResponse:
    """
        Enhanced variable extraction with SKEMA tool support.
    """
    contents = await file.read()
    key = gpt_key
    # Assuming the file contains text, you can print it out
    logging.log(contents.decode())
    res_file = save_file_to_cache(file.filename, contents, "/tmp/askem")
    logging.log("file exist: ", os.path.isfile("/tmp/askem/"+res_file))
    return await async_mit_extraction_enhanced_restAPI(res_file, key, "/tmp/askem", kg_domain.value)

from typing import List
from pydantic import BaseModel

class EntityEntry(BaseModel):
    id : str
    names : Optional[List[str]]
    values : Optional[List[str]]

class ScenarioEntry(BaseModel):
    location: str
    entities: List[EntityEntry]

import jmespath as jp
import pandas as pd
from functools import reduce
import json

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage

def list_scenarios_local(gpt_key : str, extractions : dict, return_early : bool = False) -> pd.DataFrame:
    var_extractor_expr = """
        outputs[0].data.attributes[? type == 'anchored_entity'][].payload
            .{
               id:id.id,
               name:mentions[0].name
               value:value_descriptions[0].value.amount
               passage:mentions[0].extraction_source.surrounding_passage
            }
    """
    df_entities = pd.DataFrame(jp.search(var_extractor_expr.replace('\n', ' '), extractions))

    ## extracts key fields from all the scenario context entries
    location_expr = """
        outputs[0].data.attributes[? type == 'scenario_context'][][].payload
            .{  references:extractions[].id,
                location:location.location }
    """
    loc_refs = jp.search(location_expr.replace('\n', ' '), extractions)

    tmp1 = map(lambda rec : [{'references':ref, 'location':rec['location']} for ref in rec['references'] ], loc_refs)
    tmp2 = reduce(lambda x,y : x+y, tmp1, [])
    df_scenarios = pd.DataFrame(tmp2)
    df_scenarios = df_scenarios.dropna() # remove any null references
    df_ans = df_scenarios.merge(df_entities, left_on='references', right_on='id', how='inner')
    df_ans = df_ans.drop(columns=['references'])
    df2 = df_ans
    df3 = df2[~df2.value.isna()]
    df4 = df3[df3.value.map(lambda x : is_float(x.strip()))]
    df4 = df4.assign(value=df4.value.map(lambda x : float(x.strip())))
    df4 = df4[df4.name.map(lambda x : ' ' not in x.strip())]

    if return_early:
        return df4

    context = df4.passage.unique()

    model = 'gpt-3.5-turbo'
    model = 'gpt-4'
    key = os.environ['OPENAI_API_KEY']
    llm = ChatOpenAI(model_name=model, openai_api_key=key, temperature=0)
        # prompt = """
        #     Here is a section of text that describes certain variables, their values, and geographic contexts in which the variable holds a certain value.
        #     Please extract a table of three columns: VARNAME, VALUE, and GEO.
        #     Please just report the variable names as they appear in the text. In some cases a variable might have multiple observed values for a particular geography.
        #     A row in this table should reflect the claims made in the below text.
        #     Here is the text: {excerpt}
        # """.format(excerpt=c)
        # prompt = f"""
        #             Here is a section of text that describes certain variables, their values, and geographic contexts in which the variable holds a certain value.  Please extract a table of three columns: VARNAME, VALUE, and GEO.  Please just report the variable names as they appear in the text. In some cases a variable might have multiple observed values for a particular geography.
        #             A row in this table should reflect the claims made in the below text.
        #             The text starts after the dashed line:
        #             --------------
        #             {c}
        #         """

    results = []
    for c in context:
        prompt = """
            Here is a section of text.
            The text may describe certain numerical parameters and their values for mathematical models.
            We want to extract these variables with their geographic contexts when they are available.
            When there are variables in the text, please extract a json list of records with fields with the following structure
            {{
                varname: variable name as it appears in the text,
                value: a single observed numerical value for this variable,
                geo: a single geographic location in which the variable holds this value
            }}

            If there are multiple values for the same location, include multiple records for that location.

            If there are no meaningful variables, or the text does not seem  to refer to variables of a mathematical model,
            please just return an empty list.

            Here is the text: {excerpt}
        """.format(excerpt=c)

        completion = llm.invoke(input=[HumanMessage(content=prompt)])

        results.append(completion.content)


    acc = []
    for r in results:
        ret = json.loads(r)
        acc += ret
    return pd.DataFrame(acc).drop_duplicates()

@router.post("/list_scenarios/", tags=["Paper-2-annotated-vars"])
async def list_scenarios(gpt_key: str, extractions_file: UploadFile = File(...)):
    """
        Produce scenario summary from SKEMA integrated-pdf-extractions.
        Currently only supporting locations.
        Pass in the response.json()  endpoint as a file upload.
    """
    logging.info('hello')
    extractions = json.loads((await extractions_file.read()).decode())
    df = list_scenarios_local(gpt_key, extractions)
    return JSONResponse(content=df.to_dict(orient='records'))
