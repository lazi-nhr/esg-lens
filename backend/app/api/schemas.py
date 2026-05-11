"""
Request and response schemas for the API.
"""
from pydantic import BaseModel, validator
from typing import List, Optional


class DocumentCreateRequest(BaseModel):
    content: str

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        if len(v) > 10000:
            raise ValueError('Content exceeds maximum length of 10000 characters')
        return v


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v

    @validator('top_k')
    def validate_top_k(cls, v):
        if v < 1 or v > 100:
            raise ValueError('top_k must be between 1 and 100')
        return v


class EvaluateRequest(BaseModel):
    company: str
    criterion: str
    query: str
    top_k: int = 3
    format: str = "markdown"

    @validator('company')
    def validate_company(cls, v):
        if not v or not v.strip():
            raise ValueError('company cannot be empty')
        return v

    @validator('criterion')
    def validate_criterion(cls, v):
        if not v or not v.strip():
            raise ValueError('criterion cannot be empty')
        return v

    @validator('query')
    def validate_evaluate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('query cannot be empty')
        return v

    @validator('top_k')
    def validate_evaluate_top_k(cls, v):
        if v < 1 or v > 100:
            raise ValueError('top_k must be between 1 and 100')
        return v

    @validator('format')
    def validate_format(cls, v):
        if v not in {"markdown", "text"}:
            raise ValueError("format must be 'markdown' or 'text'")
        return v


class DocumentResponse(BaseModel):
    id: int
    content: str
    created_at: str


class QueryResponse(BaseModel):
    query: str
    results: List[dict]
    response: str


class EvaluateResponse(BaseModel):
    company: str
    criterion: str
    query: str
    retrieved_count: int
    report: str
    format: str


class HealthResponse(BaseModel):
    status: str
    database: str
