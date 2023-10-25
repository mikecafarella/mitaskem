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

@router.get("/get_sha", tags=["Debugging"])
async def get_sha():
    commit_sha = os.getenv('GIT_COMMIT_SHA', 'unknown')
    version = os.getenv('APP_VERSION', 'unknown')
    return {"mitaskem_commit_sha": commit_sha, "mitaskem_image_version": version}