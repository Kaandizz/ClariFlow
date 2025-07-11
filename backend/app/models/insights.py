from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class DataSourceType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    DATABASE = "database"
    API = "api"
    DASHBOARD = "dashboard"

class InsightType(str, Enum):
    TREND = "trend"
    CORRELATION = "correlation"
    OUTLIER = "outlier"
    FORECAST = "forecast"
    SUMMARY = "summary"
    COMPARISON = "comparison"
    PATTERN = "pattern"

class InsightQuery(BaseModel):
    """Request model for insight generation"""
    question: str = Field(..., description="Natural language question about the data")
    data_source: str = Field(..., description="Identifier for the data source (file path, database table, etc.)")
    data_source_type: DataSourceType = Field(..., description="Type of data source")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters to apply to the data")
    visualization_type: Optional[str] = Field(default=None, description="Type of visualization to generate (chart, table, etc.)")
    analysis_type: Optional[str] = Field(default=None, description="Type of advanced analysis to perform (regression, clustering, forecasting)")

class InsightResponse(BaseModel):
    """Response model for insight generation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    insight_type: InsightType
    data_source: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.now)
    visualization_data: Optional[Dict[str, Any]] = Field(default=None, description="Data for generating visualizations")
    supporting_data: Optional[Dict[str, Any]] = Field(default=None, description="Supporting data and statistics")
    recommendations: Optional[List[str]] = Field(default=None, description="Actionable recommendations based on the insight")

class DataSourceInfo(BaseModel):
    """Information about available data sources"""
    id: str
    name: str
    type: DataSourceType
    description: Optional[str] = None
    columns: Optional[List[str]] = None
    row_count: Optional[int] = None
    last_updated: Optional[datetime] = None
    file_size: Optional[int] = None

class DataSourceList(BaseModel):
    """List of available data sources"""
    sources: List[DataSourceInfo]
    total_count: int 