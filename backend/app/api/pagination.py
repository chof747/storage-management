from typing import List, Tuple
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy import text
from sqlalchemy.orm import Query as SQLQuery


class PageQueryParameters(BaseModel):
    limit: int = Query(10, ge=0, le=100)
    offset: int = Query(0, ge=0)
    filter: List[str] = Query(
        [], description="Filter in the format key:value. E.g., category:resistor"
    )

    def filtering(self, query: SQLQuery) -> SQLQuery:
        for f in self.filter or []:
            key, value = f.split(":", 1)
            query = query.filter(text(f"`{key}` LIKE '%{value}%'"))
        return query

    def __call__(self, query: SQLQuery) -> Tuple[int, SQLQuery]:
        filtered = self.filtering(query)
        total: int = filtered.count()
        return (total, filtered.offset(self.offset).limit(self.limit))


def page_parameters(
    limit: int = Query(10, ge=0, le=100),
    offset: int = Query(0, ge=0),
    filter: List[str] = Query([]),
) -> PageQueryParameters:

    return PageQueryParameters(limit=limit, offset=offset, filter=filter)
