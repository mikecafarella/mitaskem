import os
import sys
import ast
from pathlib import Path

from fastapi import APIRouter, status, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from askem_extractions.data_model import *
from askem_extractions.importers import import_arizona, import_mit
from askem_extractions.importers.mit import categorize_attributes

from mitaskem.src.file_cache import save_file_to_cache
from mitaskem.src.mit_extraction import mit_extraction_restAPI, load_concise_vars, load_arizona_concise_vars, \
    build_map_from_concise_vars

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


router = APIRouter()

def merge_collections(a_collection: AttributeCollection, m_collection: AttributeCollection,
                      map_path: Path) -> AttributeCollection:
    # Extract the data from json file
    # Load mapping file
    with open(map_path, "r") as mapping_file:
        mappings = mapping_file.readlines()

    # Parse the mappings into a dictionary
    mapping_dict = {}
    for mapping in mappings:
        key,value = mapping.strip().split(", ")
        mapping_dict[key] = value.strip('"').strip(",")

    az_anchored_extractions, az_docs, az_context = categorize_attributes(a_collection)
    mit_anchored_extractions, mit_docs, _ = categorize_attributes(m_collection)

    az_docs = az_docs[0]
    mit_docs = mit_docs[0]

    for vs in (a.payload for a in az_anchored_extractions):
        entry_b_id = vs.id.id
        # print(entry_b_id)
        if entry_b_id in mapping_dict.values():
            # print("Found mapping")
            # Get the corresponding key (id from data_a) and find the entry in data_a
            entry_a_id = [k for k, v in mapping_dict.items() if v == entry_b_id][0]

            for entry_a in (a.payload for a in mit_anchored_extractions):
                if entry_a.id.id == entry_a_id:
                    # TODO Figure out what to do with the metadata
                    for name in entry_a.mentions:
                        vs.mentions.append(name)
                    if entry_a.text_descriptions:
                        for d in entry_a.text_descriptions:
                            vs.text_descriptions.append(d)
                    if entry_a.groundings:
                        # iterate through the list of dkg_annotations
                        for term in entry_a.groundings:
                            vs.groundings.append(term)
                    # if entry_a.variable.column is not empty
                    if entry_a.data_columns:
                        # iterate through the list of data_annotations
                        for term in entry_a.data_columns:
                            if not vs.data_columns:
                                vs.data_columns = list()
                            vs.data_columns.append(term)
                    if entry_a.value_descriptions:
                        for value in entry_a.value_descriptions:
                            if not vs.value_descriptions:
                                vs.value_descriptions = list()
                            vs.value_descriptions.append(value)

    merged_docs = Attribute(type=AttributeType.document_collection, payload=DocumentCollection(documents=az_docs.payload.documents + mit_docs.payload.documents))

    return AttributeCollection(attributes=az_anchored_extractions + [merged_docs] + az_context)


@router.post("/get_mapping", tags=["TA1-Integration"], response_model=AttributeCollection)
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
    # load arizona contents as json file
    a_josn = json.loads(arizona_contents.decode())
    if 'outputs' in a_josn:
        print("Arizona input includes wrapper, removing wrapper...")
        a_josn = a_josn['outputs'][0]['data']

    # Assuming the file contains text, you can print it out
    arizona_str = json.dumps(a_josn)
    res_arizona_file = save_file_to_cache(arizona_file.filename, arizona_str.encode(), "/tmp/askem")
    arizona_concise = res_arizona_file.replace(".json", "-concise.txt")
    print("file exist: ", os.path.isfile("/tmp/askem/" + res_arizona_file))
    load_arizona_concise_vars(
        os.path.join(cache_dir, res_arizona_file),
        os.path.join(cache_dir, arizona_concise))
    mit_text = open(os.path.join(cache_dir, mit_concise)).read()
    arizona_text = open(os.path.join(cache_dir, arizona_concise)).read()
    print("=========mit text: ", mit_text)
    print("=========arizona text: ", arizona_text)

    mit_arizona_map = build_map_from_concise_vars(mit_text, arizona_text,key)

    map_file = res_mit_file.replace(".json", "-map.txt")
    print("GPT map output: ", mit_arizona_map)
    open(os.path.join(cache_dir, map_file), "w").write(mit_arizona_map)
    print("map file: ", mit_arizona_map)
    print("map file ends here.")

    a_collection = AttributeCollection.from_json(Path(os.path.join(cache_dir, res_arizona_file)))
    m_collection = AttributeCollection.from_json(Path(os.path.join(cache_dir, res_mit_file)))
    merged = merge_collections(a_collection, m_collection,
                                Path(os.path.join(cache_dir, map_file)))
    # integreated_file = res_mit_file.split("mit-")[0] + "-integrated.json"
    # merged.save_json(os.path.join(cache_dir, integreated_file))
    # integreated_json = open(os.path.join(cache_dir, integreated_file)).read()
    return merged


if __name__ == "__main__":
    GPT_KEY = None 
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
    print('map ', mit_arizona_map)
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
