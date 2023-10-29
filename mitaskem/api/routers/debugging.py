import os
import sys

from fastapi import APIRouter, status, UploadFile, File, HTTPException


sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


router = APIRouter()

@router.get("/get_sha", tags=["Debugging"])
async def get_sha():
    commit_sha = os.getenv('GIT_COMMIT_SHA', 'unknown')
    version = os.getenv('APP_VERSION', 'unknown')
    return {"mitaskem_commit_sha": commit_sha, "mitaskem_image_version": version}