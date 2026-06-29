from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.schemas.upload import UploadResponse
from app.services.upload import UploadService
from app.utils.security import sanitize_filename

router = APIRouter(prefix="/upload", tags=["文件上传"])

_MAX_SIZE = settings.max_upload_size_mb * 1024 * 1024


def _check_file_size(file: UploadFile) -> None:
    if file.size is not None and file.size > _MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large")


@router.post("/dataset", response_model=UploadResponse, summary="上传数据集压缩包")
async def upload_dataset(file: UploadFile = File(...)):
    _check_file_size(file)
    filename = sanitize_filename(file.filename or "dataset.zip", "dataset.zip")
    service = UploadService()
    try:
        path = await service.save_dataset_archive(filename, file.file)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e
    return UploadResponse(
        filename=filename,
        file_path=path,
        size_bytes=file.size or 0,
    )


@router.post("/model-weight", response_model=UploadResponse, summary="上传模型权重文件")
async def upload_model_weight(file: UploadFile = File(...)):
    _check_file_size(file)
    filename = sanitize_filename(file.filename or "model.pt", "model.pt")
    service = UploadService()
    try:
        path = await service.save_model_weight(filename, file.file)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e
    return UploadResponse(
        filename=filename,
        file_path=path,
        size_bytes=file.size or 0,
    )


@router.post("/image", response_model=UploadResponse, summary="上传推理图片")
async def upload_image(file: UploadFile = File(...)):
    _check_file_size(file)
    filename = sanitize_filename(file.filename or "image.jpg", "image.jpg")
    service = UploadService()
    try:
        path = await service.save_image(filename, file.file)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e
    return UploadResponse(
        filename=filename,
        file_path=path,
        size_bytes=file.size or 0,
    )
