import os
import sys

from fastapi import APIRouter, status, UploadFile, File, HTTPException


sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


router = APIRouter()

from pydantic import BaseModel

class ShaResponse(BaseModel):
    mitaskem_commit_sha: str
    mitaskem_image_version: str

@router.get("/get_sha", tags=["Debugging"], response_model=ShaResponse)
async def get_sha():
    commit_sha = os.getenv('GIT_COMMIT_SHA', 'unknown')
    version = os.getenv('APP_VERSION', 'unknown')
    return {"mitaskem_commit_sha": commit_sha, "mitaskem_image_version": version}