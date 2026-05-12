from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from database import get_db
from models import PageVisit
from datetime import datetime, timezone

router = APIRouter(prefix="/stats", tags=["统计"])


@router.post("/visit", status_code=201)
def record_visit(request: Request, db: Session = Depends(get_db)):
    db.add(PageVisit())
    db.commit()
    return {}


@router.get("")
@router.get("/")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(PageVisit.id)).scalar()

    today = datetime.now(timezone.utc).date()
    today_count = db.query(func.count(PageVisit.id)).filter(
        cast(PageVisit.created_at, Date) == today
    ).scalar()

    # 最近 7 天每日访问量
    daily = db.query(
        cast(PageVisit.created_at, Date).label("date"),
        func.count(PageVisit.id).label("count")
    ).group_by("date").order_by("date").limit(7).all()

    return {
        "total": total,
        "today": today_count,
        "daily": [{"date": str(r.date), "count": r.count} for r in daily]
    }
