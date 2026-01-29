"""Pydantic models used by the Notes API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Shared fields for note create/update operations."""

    title: str = Field(..., min_length=1, description="Short title for the note.")
    content: str = Field(..., min_length=1, description="Full note content.")


class NoteCreate(NoteBase):
    """Request body for creating a note."""


class NoteUpdate(BaseModel):
    """Request body for updating a note (partial updates supported via PUT)."""

    title: Optional[str] = Field(None, min_length=1, description="Updated title.")
    content: Optional[str] = Field(None, min_length=1, description="Updated content.")


class Note(NoteBase):
    """Response model for a persisted note."""

    id: int = Field(..., description="Auto-incrementing note identifier.")
    created_at: str = Field(..., description="ISO-like datetime string when the note was created.")
    updated_at: str = Field(..., description="ISO-like datetime string when the note was last updated.")
