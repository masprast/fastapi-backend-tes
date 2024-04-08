from datetime import datetime
import hashlib
import os
import shutil
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path

from app.service.uploadService import fileValidator


router = APIRouter(prefix="/files", tags=["File"])


def lokasi(tgl: str, file: str):
    path = f"files/{tgl}/{file}"
    return path


@router.get("/", summary="format tanggal: YYYY-MM-DD, contoh: 2024-04-08")
async def view(f: Annotated[UploadFile, Depends(lokasi)]):
    # file = lokasi(datetime.now().strftime("%Y-%m-%d"), f.filename)
    file = Path(f).absolute()
    if not file.is_file():
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT, detail=f"file tidak diketahui"
        )
    return FileResponse(
        file,
        headers={
            "content-disposition": f"attachment; filename = {file.name}",
            "content-type": "application/video;application/image",
            "produces": "image/png;video/mp4",
        },
    )


@router.post("/upload")
async def upload(
    ufile: Annotated[UploadFile, Form],
):
    fileValidator(ufile)
    sekarang = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(f"files/{sekarang}"):
        os.makedirs(f"files/{sekarang}")

    if not ufile:
        return {"pesan": "tidak ada file yang di-upload"}
    nama_file_encrypted = (
        f"""{generateNamaFile(ufile.filename)}.{ufile.content_type.split('/')[1]}"""
    )
    path = f"""files/{sekarang}/{nama_file_encrypted}"""
    with open(path, "bw") as file:
        shutil.copyfileobj(ufile.file, file)

    return {
        "file": ufile.filename,
        "ukuran": ufile.size,
        "jenis": ufile.content_type,
        "lokasi": path,
    }


def generateNamaFile(file: str):
    file_str = hashlib.md5(file.encode("UTF-8")).hexdigest()
    return str(UUID(hex=file_str).hex.replace("-", ""))
