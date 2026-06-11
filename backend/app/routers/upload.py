from fastapi import APIRouter, UploadFile, File

from app.schemas.upload import UploadResponse
from app.services.upload import UploadService

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/dataset", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    content = await file.read()
    service = UploadService()
    path = await service.save_dataset_archive(file.filename or "dataset.zip", content)
    return UploadResponse(
        filename=file.filename or "dataset.zip",
        file_path=path,
        size_bytes=len(content),
    )


@router.post("/model-weight", response_model=UploadResponse)
async def upload_model_weight(file: UploadFile = File(...)):
    content = await file.read()
    service = UploadService()
    path = await service.save_model_weight(file.filename or "model.pt", content)
    return UploadResponse(
        filename=file.filename or "model.pt",
        file_path=path,
        size_bytes=len(content),
    )


@router.post("/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    service = UploadService()
    path = await service.save_image(file.filename or "image.jpg", content)
    return UploadResponse(
        filename=file.filename or "image.jpg",
        file_path=path,
        size_bytes=len(content),
    )
