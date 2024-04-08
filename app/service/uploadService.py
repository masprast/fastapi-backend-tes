from annotated_types import LowerCase
import filetype
from fastapi import HTTPException, UploadFile, status


def fileValidator(file: UploadFile):
    FILE_SIZE = 5012983

    ekstensi = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/tiff",
        "image/bmp",
        "video/webm",
        "video/mp4",
    }
    file_info = filetype.guess(file.file).mime
    # print(file_info, file.content_type)
    if file_info not in ekstensi or file_info is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"file {file_info} tidak dikenali",
        )

    if file.content_type not in ekstensi:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="file tidak didukung",
        )

    ukuranFile = 0
    for chunk in file.file:
        ukuranFile += len(chunk)
        if ukuranFile > FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="file terlalu besar",
            )
