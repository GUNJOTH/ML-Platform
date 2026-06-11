from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/annotations")
async def annotation_stats():
    return {"message": "annotation statistics placeholder"}


@router.get("/training/{task_id}")
async def training_stats(task_id: str):
    return {"task_id": task_id, "message": "training metrics placeholder"}
