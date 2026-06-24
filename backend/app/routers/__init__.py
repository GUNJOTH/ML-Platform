from fastapi import APIRouter

from app.routers.dataset import router as dataset_router
from app.routers.dataset_export import router as dataset_export_router
from app.routers.dataset_version import router as dataset_version_router
from app.routers.annotation import router as annotation_router
from app.routers.label import router as label_router
from app.routers.model import router as model_router
from app.routers.task import router as task_router
from app.routers.stats import router as stats_router
from app.routers.upload import router as upload_router
from app.routers.inference import router as inference_router
from app.routers.evaluation import router as evaluation_router
from app.routers.ws import router as ws_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(dataset_router)
api_router.include_router(dataset_version_router)
api_router.include_router(dataset_export_router)
api_router.include_router(annotation_router)
api_router.include_router(label_router)
api_router.include_router(model_router)
api_router.include_router(task_router)
api_router.include_router(stats_router)
api_router.include_router(upload_router)
api_router.include_router(inference_router)
api_router.include_router(evaluation_router)
api_router.include_router(ws_router)
