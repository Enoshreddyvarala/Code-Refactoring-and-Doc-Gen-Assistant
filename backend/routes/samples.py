"""Sample programs and file upload routes."""

from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile
from backend.schemas.models import SampleItem
from backend.utils.sample_codes import (
    SAMPLE_PROGRAMS,
    get_sample_code,
    get_sample_description,
    get_sample_names,
)

router = APIRouter(tags=["Samples & Files"])


@router.get("/samples", response_model=List[SampleItem])
async def list_sample_programs():
    """Retrieve all educational sample programs."""
    items = []
    for name in get_sample_names():
        items.append(SampleItem(
            name=name,
            description=get_sample_description(name),
            code=get_sample_code(name),
        ))
    return items


@router.get("/samples/{name}", response_model=SampleItem)
async def get_single_sample(name: str):
    """Retrieve a single sample program by name."""
    if name not in SAMPLE_PROGRAMS:
        raise HTTPException(status_code=404, detail=f"Sample '{name}' not found.")
    return SampleItem(
        name=name,
        description=get_sample_description(name),
        code=get_sample_code(name),
    )


@router.post("/upload")
async def upload_python_file(file: UploadFile = File(...)):
    """Upload and read a .py file into text."""
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python files (.py) are supported.")

    try:
        content = await file.read()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
        return {"filename": file.filename, "code": text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(exc)}")
