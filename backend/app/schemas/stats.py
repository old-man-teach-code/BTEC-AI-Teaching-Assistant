from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class StatsResponse(BaseModel):
    """Response schema cho thống kê tổng quan"""
    documents: int
    events: int
    events_today: int
    upcoming_events: int
    notifications: int
    unread_notifications: int
    documents_this_week: int
    documents_last_week: int
    document_growth: float

    class Config:
        from_attributes = True

class DocumentStatsResponse(BaseModel):
    """Response schema cho thống kê documents"""
    labels: List[str]
    data: List[int]
    total: int
    period: str

    class Config:
        from_attributes = True

class EventStatsResponse(BaseModel):
    """Response schema cho thống kê events"""
    labels: List[str]
    data: List[int]
    total: int
    period: str

    class Config:
        from_attributes = True

class ActivityStatsResponse(BaseModel):
    """Response schema cho thống kê hoạt động"""
    new_documents: int
    new_events: int
    new_notifications: int
    period_days: int

    class Config:
        from_attributes = True

class ChartDatasetResponse(BaseModel):
    """Response schema cho dataset của biểu đồ"""
    label: str
    data: List[int]
    backgroundColor: str
    borderColor: str
    borderWidth: int

class ChartDataResponse(BaseModel):
    """Response schema cho dữ liệu biểu đồ"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    chart_type: str
    period: str

    class Config:
        from_attributes = True
