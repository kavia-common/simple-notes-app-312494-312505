from __future__ import annotations

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field

from src.api.dao import create_note, delete_note, get_note, list_notes, update_note
from src.api.db import get_db
from src.api.models import Note, NoteCreate, NoteUpdate

openapi_tags = [
    {"name": "health", "description": "Service health and diagnostics."},
    {"name": "notes", "description": "CRUD operations for notes."},
]

app = FastAPI(
    title="Simple Notes API",
    description="Backend API for a simple notes app (FastAPI + SQLite).",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS:
# - Local dev: CRA runs on http://localhost:3000
# - Kavia preview: frontend is served from a https://...:3000 origin
# Since the backend URL is configurable in the frontend, we allow a small,
# explicit list of known dev origins to avoid CORS issues end-to-end.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        # Kavia preview origin for the running frontend container (port 3000)
        "https://vscode-internal-21100-beta.beta01.cloud.kavia.ai:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["health"],
    summary="Health Check",
    description="Basic health check endpoint.",
)
def health_check():
    """Return a simple health status message."""
    return {"message": "Healthy"}


@app.get(
    "/notes",
    response_model=list[Note],
    tags=["notes"],
    summary="List notes",
    description="Return all notes (newest updated first).",
    operation_id="list_notes",
)
def http_list_notes(conn=Depends(get_db)):
    """List notes."""
    return list_notes(conn)


@app.get(
    "/notes/{id}",
    response_model=Note,
    tags=["notes"],
    summary="Get note",
    description="Retrieve a note by its integer id.",
    operation_id="get_note",
)
def http_get_note(id: int = Field(..., ge=1, description="Note id"), conn=Depends(get_db)):
    """Retrieve a single note."""
    note = get_note(conn, id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create note",
    description="Create a new note.",
    operation_id="create_note",
)
def http_create_note(payload: NoteCreate, conn=Depends(get_db)):
    """Create and return a note."""
    return create_note(conn, payload)


@app.put(
    "/notes/{id}",
    response_model=Note,
    tags=["notes"],
    summary="Update note",
    description="Update a note by id. Missing fields are left unchanged.",
    operation_id="update_note",
)
def http_update_note(
    id: int = Field(..., ge=1, description="Note id"),
    payload: NoteUpdate = ...,
    conn=Depends(get_db),
):
    """Update an existing note."""
    updated = update_note(conn, id, payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated


@app.delete(
    "/notes/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["notes"],
    summary="Delete note",
    description="Delete a note by id.",
    operation_id="delete_note",
)
def http_delete_note(id: int = Field(..., ge=1, description="Note id"), conn=Depends(get_db)):
    """Delete a note."""
    ok = delete_note(conn, id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
