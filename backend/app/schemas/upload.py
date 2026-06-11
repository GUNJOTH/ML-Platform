from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    file_path: str
    size_bytes: int


class DatasetImportRequest(BaseModel):
    name: str
    description: str | None = None
    data_type: str = "image"
