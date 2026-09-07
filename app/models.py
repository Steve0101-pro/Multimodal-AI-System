import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import MappedColumn,mapped_column,relationship
from sqlalchemy.dialects.postgresql import UUID,JSONB
from datetime import datetime
from app.database import Base
from typing import Any, Optional



class User(Base):

    __tablename__ = "users"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,)

    email: MappedColumn[str] = mapped_column(String(255),unique=True,index=True,nullable=False,)

    password_hash: MappedColumn[str] = mapped_column(String(255),nullable=False,)

    role: MappedColumn[str] = mapped_column(String(50),default="user",nullable=False,)

    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False,)

    documents = relationship("Document",back_populates="owner",)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash: MappedColumn[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: MappedColumn[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)







class Document(Base):

    __tablename__ = "documents"

    id : MappedColumn[uuid.UUID] = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,index=True)

    user_id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # ADD THIS
    
    filename:MappedColumn[str] = mapped_column(String(255),nullable=False,)

    content_type: MappedColumn[str] = mapped_column(String(100),nullable=False,)

    layout_data: MappedColumn[Optional[dict[str,Any]]] = mapped_column(JSONB,nullable=True,)
     
    storage_path: MappedColumn[str] = mapped_column(String(500),nullable=False,)

    extracted_text: MappedColumn[str] = mapped_column(Text,nullable=True,)

    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False,)

    owner = relationship("User",back_populates="documents",)


class Conversation(Base):

    __tablename__ = "conversations"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,)

    user_id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False,)

    title: MappedColumn[str | None] = mapped_column(String(255),nullable=True,)

    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),server_default=func.now(),nullable=False,)


class Message(Base):

    __tablename__ = "messages"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,)

    conversation_id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("conversations.id"),nullable=False,index=True,)

    role: MappedColumn[str] = mapped_column(String(50),nullable=False,)

    content: MappedColumn[str] = mapped_column(Text,nullable=False,)

    metadata_json: MappedColumn[dict | None] = mapped_column(JSONB,nullable=True,)

    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False,)


class ResponseFeedback(Base):
    __tablename__ = "response_feedback"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    conversation_id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    rating: MappedColumn[int | None] = mapped_column(nullable=True)
    comment: MappedColumn[str | None] = mapped_column(Text, nullable=True)
    review_status: MappedColumn[str] = mapped_column(String(30), nullable=False, server_default="pending")
    reviewer_notes: MappedColumn[str | None] = mapped_column(Text, nullable=True)
    model_version: MappedColumn[str] = mapped_column(String(150), nullable=False)
    prompt_version: MappedColumn[str] = mapped_column(String(80), nullable=False)
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: MappedColumn[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action: MappedColumn[str] = mapped_column(String(80), nullable=False)
    resource_type: MappedColumn[str] = mapped_column(String(80), nullable=False)
    resource_id: MappedColumn[str | None] = mapped_column(String(150), nullable=True)
    metadata_json: MappedColumn[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class TTSRecord(Base):
    __tablename__ = "tts_records"
    id: MappedColumn[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)    
    text: MappedColumn[str] = mapped_column(Text, nullable=False)    
    storage_path: MappedColumn[str] = mapped_column(String(500), nullable=False)
    reference_filename: MappedColumn[str] = mapped_column(String(255), nullable=False)
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)




