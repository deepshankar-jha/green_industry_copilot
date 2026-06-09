from fastapi import APIRouter, UploadFile, File
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_files(
        files: list[UploadFile] = File(...)
):

    saved_files = []

    for file in files:

        contents = await file.read()

        path = UPLOAD_DIR / file.filename

        with open(path, "wb") as f:
            f.write(contents)

        saved_files.append(file.filename)

    return {
        "status": "success",
        "files": saved_files
    }