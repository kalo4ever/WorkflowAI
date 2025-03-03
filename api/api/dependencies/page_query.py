from typing import Annotated, Optional

from fastapi import Depends, Query

from core.domain.page_query_mixin import PageQueryMixin


def page_query_dependency(
    limit: int = Query(None, description="The number of items to return"),
    offset: Optional[int] = Query(None, description="The number of items to skip"),
) -> PageQueryMixin:
    return PageQueryMixin(limit=limit, offset=offset)


PageQueryDep = Annotated[PageQueryMixin, Depends(page_query_dependency)]
