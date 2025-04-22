from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Query as SQLQuery

class PageQueryParameters(BaseModel):
  limit: int = Query(10, ge=0, le=100)
  offset: int = Query(0, ge=0)

  def __call__(self, query: SQLQuery) -> SQLQuery:
    return query.offset(self.offset).limit(self.limit)

def page_parameters(
    limit: int | None = None,
    offset: int | None = None) -> PageQueryParameters:
  
  return PageQueryParameters(
    limit=limit,
    offset=offset
  )

