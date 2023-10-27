import os
import sys
import ast
from pathlib import Path

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from askem_extractions.data_model import *
from askem_extractions.importers import import_arizona, import_mit
from askem_extractions.importers.mit import merge_collections

from mitaskem.src.file_cache import save_file_to_cache
from mitaskem.src.mit_extraction import mit_extraction_restAPI, load_concise_vars, load_arizona_concise_vars, \
    build_map_from_concise_vars

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


router = APIRouter()


@router.post("/get_mapping", tags=["TA1-Integration"])
async def upload_files_integration(gpt_key: str, mit_file: UploadFile = File(...), arizona_file: UploadFile = File(...)):
    """
        Upload MIT and Arizona extractions in TA1 schema, build entity mapping and align them together.
    """
    key = gpt_key
    cache_dir = "/tmp/askem"

    mit_contents = await mit_file.read()
    # Assuming the file contains text, you can print it out
    print(mit_contents.decode())
    res_mit_file = save_file_to_cache(mit_file.filename, mit_contents, cache_dir)
    mit_concise = res_mit_file.replace(".json","-concise.txt")
    print("file exist: ", os.path.isfile("/tmp/askem/"+res_mit_file))
    load_concise_vars(
        os.path.join(cache_dir, res_mit_file),
        os.path.join(cache_dir, mit_concise))

    arizona_contents = await arizona_file.read()
    # Assuming the file contains text, you can print it out
    print(arizona_contents.decode())
    res_arizona_file = save_file_to_cache(arizona_file.filename, arizona_contents, "/tmp/askem")
    arizona_concise = res_arizona_file.replace(".json", "-concise.txt")
    print("file exist: ", os.path.isfile("/tmp/askem/" + res_arizona_file))
    load_arizona_concise_vars(
        os.path.join(cache_dir, res_arizona_file),
        os.path.join(cache_dir, arizona_concise))
    mit_text = open(os.path.join(cache_dir, mit_concise)).read()
    arizona_text = open(os.path.join(cache_dir, arizona_concise)).read()

    map_file = res_mit_file.replace(".json", "-map.txt")

    mit_arizona_map = build_map_from_concise_vars(mit_text, arizona_text,key)

    print(mit_arizona_map)
    open(os.path.join(cache_dir, map_file), "w").write(mit_arizona_map)
    print("map file: ", map_file)

    a_collection = AttributeCollection.from_json(Path(os.path.join(cache_dir, res_arizona_file)))
    m_collection = AttributeCollection.from_json(Path(os.path.join(cache_dir, res_mit_file)))
    merged = merge_collections(a_collection, m_collection,
                                Path(os.path.join(cache_dir, map_file)))
    # integreated_file = res_mit_file.split("mit-")[0] + "-integrated.json"
    # merged.save_json(os.path.join(cache_dir, integreated_file))
    # integreated_json = open(os.path.join(cache_dir, integreated_file)).read()
    return merged


if __name__ == "__main__":
    GPT_KEY = os.environ.get('OPENAI_API_KEY')
    key = GPT_KEY
    cache_dir = "/Users/chunwei/research/mitaskem/resources/xDD/"

    res_mit_file = "mit-extraction/bucky__mit-extraction_id.json"
    mit_concise = res_mit_file.replace(".json", "-concise.txt")
    # print("file exist: ", os.path.isfile("/tmp/askem/" + res_mit_file))
    load_concise_vars(
        os.path.join(cache_dir, res_mit_file),
        os.path.join(cache_dir, mit_concise))

    res_arizona_file = "arizona-extraction/bucky_arizona_output_example.json"
    arizona_concise = res_arizona_file.replace(".json", "-concise.txt")

    load_arizona_concise_vars(
        os.path.join(cache_dir, res_arizona_file),
        os.path.join(cache_dir, arizona_concise))
    mit_text = open(os.path.join(cache_dir, mit_concise)).read()
    arizona_text = open(os.path.join(cache_dir, arizona_concise)).read()
    print("mit text: ", mit_text)
    print("arizona text: ", arizona_text)
    print("res_mit_file: ", res_mit_file)

    map_file = res_mit_file.split("_mit-")[0] + "-map.txt"

    mit_arizona_map = build_map_from_concise_vars(mit_text, arizona_text, key)
    print(mit_arizona_map)
    open(os.path.join(cache_dir, map_file), "w").write(mit_arizona_map)
    print("map file: ", map_file)


    a_collection = import_arizona(Path(os.path.join(cache_dir, res_arizona_file)))
    m_collection = import_mit(Path(os.path.join(cache_dir, res_mit_file)))
    merged = merge_collections(a_collection, m_collection,
                               Path(os.path.join(cache_dir, map_file)))
    integreated_file = res_mit_file.split("mit-")[0] + "-integrated.json"
    merged.save_json(os.path.join(cache_dir, integreated_file))
    integreated_json = open(os.path.join(cache_dir, integreated_file)).read()
    # print({"file name": integreated_file, "file contents": integreated_json})
