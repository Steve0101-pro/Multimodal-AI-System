"""User feedback and human-review queue endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Conversation, ResponseFeedback, User
from app.schema import FeedbackCreate, FeedbackResponse, FeedbackReviewUpdate
from app.services.metrics import FEEDBACK
from app.services.experiments import assign_variant
from app.services.audit import record_audit
from app.services.safety import redact_sensitive_text

router = APIRouter(prefix="/feedback", tags=["Feedback & Review"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    payload: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == payload.conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    feedback_data = payload.model_dump()
    if feedback_data.get("comment"):
        feedback_data["comment"] = redact_sensitive_text(feedback_data["comment"])
    feedback = ResponseFeedback(**feedback_data, user_id=current_user.id)
    FEEDBACK.labels(str(payload.rating), assign_variant(str(current_user.id))).inc()
    await record_audit(
        db,
        action="feedback.created",
        resource_type="response_feedback",
        actor_id=current_user.id,
        resource_id=str(feedback.id),
        metadata={"rating": payload.rating},
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/review-queue", response_model=list[FeedbackResponse])
async def list_review_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    result = await db.execute(
        select(ResponseFeedback)
        .where(ResponseFeedback.review_status == "pending")
        .order_by(ResponseFeedback.created_at.asc())
        .limit(100)
    )
    return result.scalars().all()


@router.patch("/{feedback_id}/review", response_model=FeedbackResponse)
async def review_feedback(
    feedback_id: UUID,
    payload: FeedbackReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    feedback = await db.get(ResponseFeedback, feedback_id)
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")

    feedback.review_status = payload.review_status
    feedback.reviewer_notes = (
        redact_sensitive_text(payload.reviewer_notes)
        if payload.reviewer_notes
        else None
    )
    await record_audit(
        db,
        action="feedback.reviewed",
        resource_type="response_feedback",
        actor_id=current_user.id,
        resource_id=str(feedback.id),
        metadata={"review_status": payload.review_status},
    )
    await db.commit()
    await db.refresh(feedback)
    return feedback