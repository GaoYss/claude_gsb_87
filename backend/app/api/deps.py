"""接口层公共依赖。"""

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


class Pagination:
    """统一分页参数。"""

    def __init__(
        self,
        page: int = Query(1, ge=1, le=10000, description="页码，从 1 开始"),
        page_size: int = Query(
            settings.default_page_size,
            ge=1,
            le=settings.max_page_size,
            description="每页条数",
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


DbSession = Annotated[Session, Depends(get_db)]
PageParams = Annotated[Pagination, Depends()]

