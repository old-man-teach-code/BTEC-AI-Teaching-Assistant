from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dependencies.deps import get_db, get_current_user
from models.user import User
from models.document import Document, DocumentStatus
from models.event import Event
from models.notification import Notification
from schemas.stats import (
    StatsResponse, 
    DocumentStatsResponse, 
    EventStatsResponse,
    ActivityStatsResponse,
    ChartDataResponse
)

router = APIRouter()

@router.get("/health", summary="Health check cho stats API")
def stats_health_check():
    """Simple health check endpoint để test stats API"""
    return {"status": "ok", "message": "Stats API is working"}

@router.get("/", response_model=StatsResponse, summary="Lấy thống kê tổng quan")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê tổng quan cho dashboard
    """
    try:
        # Thống kê documents
        total_documents = db.query(Document).filter(
            Document.owner_id == current_user.id,
            Document.status.in_([DocumentStatus.UPLOADED.value, DocumentStatus.READY.value])
        ).count()
        
        # Thống kê events
        total_events = db.query(Event).filter(
            Event.owner_id == current_user.id
        ).count()
        
        # Events hôm nay
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        events_today = db.query(Event).filter(
            Event.owner_id == current_user.id,
            Event.start_time >= today_start,
            Event.start_time <= today_end
        ).count()
        
        # Events sắp tới (7 ngày tới)
        next_week = datetime.now() + timedelta(days=7)
        upcoming_events = db.query(Event).filter(
            Event.owner_id == current_user.id,
            Event.start_time >= datetime.now(),
            Event.start_time <= next_week
        ).count()
        
        # Thống kê notifications
        total_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).count()
        
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.event_status == 'unread'
        ).count()
        
        # Documents trong tuần này
        week_ago = datetime.now() - timedelta(days=7)
        documents_this_week = db.query(Document).filter(
            Document.owner_id == current_user.id,
            Document.created_at >= week_ago,
            Document.status.in_([DocumentStatus.UPLOADED.value, DocumentStatus.READY.value])
        ).count()

        # Documents tuần trước
        two_weeks_ago = datetime.now() - timedelta(days=14)
        documents_last_week = db.query(Document).filter(
            Document.owner_id == current_user.id,
            Document.created_at >= two_weeks_ago,
            Document.created_at < week_ago,
            Document.status.in_([DocumentStatus.UPLOADED.value, DocumentStatus.READY.value])
        ).count()
        
        # Tính growth rate
        document_growth = 0
        if documents_last_week > 0:
            document_growth = ((documents_this_week - documents_last_week) / documents_last_week) * 100
        elif documents_this_week > 0:
            document_growth = 100
            
        return StatsResponse(
            documents=total_documents,
            events=total_events,
            events_today=events_today,
            upcoming_events=upcoming_events,
            notifications=total_notifications,
            unread_notifications=unread_notifications,
            documents_this_week=documents_this_week,
            documents_last_week=documents_last_week,
            document_growth=round(document_growth, 1)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lấy thống kê: {str(e)}"
        )

@router.get("/documents", response_model=DocumentStatsResponse, summary="Thống kê documents")
def get_document_stats(
    period: str = Query("week", description="Khoảng thời gian: week, month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê documents theo thời gian
    """
    try:
        # Xác định khoảng thời gian
        if period == "week":
            days = 7
            periods = 4  # 4 tuần
        elif period == "month":
            days = 30
            periods = 6  # 6 tháng
        else:
            days = 7
            periods = 4
            
        stats = []
        labels = []
        
        for i in range(periods):
            # Fix: Tính đúng khoảng thời gian
            end_date = datetime.now() - timedelta(days=days * i)
            start_date = end_date - timedelta(days=days)

            # Fix: Sử dụng <= để bao gồm end_date
            count = db.query(Document).filter(
                Document.owner_id == current_user.id,
                Document.created_at >= start_date,
                Document.created_at <= end_date,
                Document.status.in_([DocumentStatus.UPLOADED.value, DocumentStatus.READY.value])
            ).count()

            print(f"[DEBUG] Week {periods - i}: {start_date} to {end_date} = {count} documents")
            stats.insert(0, count)
            
            if period == "week":
                labels.insert(0, f"Week {periods - i}")
            else:
                labels.insert(0, start_date.strftime("%b %Y"))
        
        return DocumentStatsResponse(
            labels=labels,
            data=stats,
            total=sum(stats),
            period=period
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lấy thống kê documents: {str(e)}"
        )

@router.get("/events", response_model=EventStatsResponse, summary="Thống kê events")
def get_event_stats(
    period: str = Query("week", description="Khoảng thời gian: week, month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê events theo thời gian
    """
    try:
        # Xác định khoảng thời gian
        if period == "week":
            days = 7
            periods = 4  # 4 tuần
        elif period == "month":
            days = 30
            periods = 6  # 6 tháng
        else:
            days = 7
            periods = 4
            
        stats = []
        labels = []
        
        for i in range(periods):
            # Fix: Tính đúng khoảng thời gian
            end_date = datetime.now() - timedelta(days=days * i)
            start_date = end_date - timedelta(days=days)

            # Fix: Sử dụng <= để bao gồm end_date
            count = db.query(Event).filter(
                Event.owner_id == current_user.id,
                Event.created_at >= start_date,
                Event.created_at <= end_date
            ).count()

            print(f"[DEBUG] Events Week {periods - i}: {start_date} to {end_date} = {count} events")
            stats.insert(0, count)
            
            if period == "week":
                labels.insert(0, f"Week {periods - i}")
            else:
                labels.insert(0, start_date.strftime("%b %Y"))
        
        return EventStatsResponse(
            labels=labels,
            data=stats,
            total=sum(stats),
            period=period
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lấy thống kê events: {str(e)}"
        )

@router.get("/activity", response_model=ActivityStatsResponse, summary="Thống kê hoạt động")
def get_activity_stats(
    days: int = Query(7, description="Số ngày gần đây"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê hoạt động gần đây
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Documents được tạo
        new_documents = db.query(Document).filter(
            Document.owner_id == current_user.id,
            Document.created_at >= start_date,
            Document.status.in_([DocumentStatus.UPLOADED.value, DocumentStatus.READY.value])
        ).count()
        
        # Events được tạo
        new_events = db.query(Event).filter(
            Event.owner_id == current_user.id,
            Event.created_at >= start_date
        ).count()
        
        # Notifications
        new_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.created_at >= start_date
        ).count()
        
        return ActivityStatsResponse(
            new_documents=new_documents,
            new_events=new_events,
            new_notifications=new_notifications,
            period_days=days
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lấy thống kê hoạt động: {str(e)}"
        )

@router.get("/chart-data", response_model=ChartDataResponse, summary="Dữ liệu cho biểu đồ")
def get_chart_data(
    chart_type: str = Query("events", description="Loại biểu đồ: events, documents, activity"),
    period: str = Query("week", description="Khoảng thời gian: week, month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy dữ liệu cho các biểu đồ
    """
    try:
        if chart_type == "events":
            result = get_event_stats(period, db, current_user)
            return ChartDataResponse(
                labels=result.labels,
                datasets=[{
                    "label": "Events",
                    "data": result.data,
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 2
                }],
                chart_type=chart_type,
                period=period
            )
        elif chart_type == "documents":
            result = get_document_stats(period, db, current_user)
            return ChartDataResponse(
                labels=result.labels,
                datasets=[{
                    "label": "Documents",
                    "data": result.data,
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 2
                }],
                chart_type=chart_type,
                period=period
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Loại biểu đồ không hỗ trợ: {chart_type}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lấy dữ liệu biểu đồ: {str(e)}"
        )
