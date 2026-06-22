from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["统计分析"])


@router.get("/annotations", summary="查询标注统计占位数据")
async def annotation_stats():
    return {"message": "annotation statistics placeholder"}


@router.get("/training/{task_id}", summary="查询训练统计占位数据")
async def training_stats(task_id: str):
    return {"task_id": task_id, "message": "training metrics placeholder"}
