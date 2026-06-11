from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model import MLModel
from app.repositories.base import BaseRepository


class MLModelRepository(BaseRepository[MLModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MLModel)
