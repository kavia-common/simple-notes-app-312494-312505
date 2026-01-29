"""Data-access layer for notes."""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from src.api.models import Note, NoteCreate, NoteUpdate


def _row_to_note(row: sqlite3.Row) -> Note:
    """Convert a sqlite row into a Note model."""
    return Note(
        id=int(row["id"]),
        title=str(row["title"]),
        content=str(row["content"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


# PUBLIC_INTERFACE
def list_notes(conn: sqlite3.Connection) -> List[Note]:
    """List all notes, newest first."""
    cur = conn.execute(
        """
        SELECT id, title, content, created_at, updated_at
        FROM notes
        ORDER BY datetime(updated_at) DESC, id DESC
        """
    )
    rows = cur.fetchall()
    return [_row_to_note(r) for r in rows]


# PUBLIC_INTERFACE
def get_note(conn: sqlite3.Connection, note_id: int) -> Optional[Note]:
    """Retrieve a single note by id, or None if missing."""
    cur = conn.execute(
        """
        SELECT id, title, content, created_at, updated_at
        FROM notes
        WHERE id = ?
        """,
        (note_id,),
    )
    row = cur.fetchone()
    return _row_to_note(row) if row else None


# PUBLIC_INTERFACE
def create_note(conn: sqlite3.Connection, payload: NoteCreate) -> Note:
    """Create a new note and return it."""
    cur = conn.execute(
        """
        INSERT INTO notes (title, content)
        VALUES (?, ?)
        """,
        (payload.title, payload.content),
    )
    conn.commit()
    new_id = int(cur.lastrowid)
    created = get_note(conn, new_id)
    # Should not be None after insert; guard anyway.
    if created is None:
        raise sqlite3.IntegrityError("Failed to read back created note")
    return created


# PUBLIC_INTERFACE
def update_note(conn: sqlite3.Connection, note_id: int, payload: NoteUpdate) -> Optional[Note]:
    """
    Update an existing note and return updated note.
    Returns None if the note doesn't exist.
    """
    existing = get_note(conn, note_id)
    if existing is None:
        return None

    new_title = payload.title if payload.title is not None else existing.title
    new_content = payload.content if payload.content is not None else existing.content

    conn.execute(
        """
        UPDATE notes
        SET title = ?, content = ?
        WHERE id = ?
        """,
        (new_title, new_content, note_id),
    )
    conn.commit()
    return get_note(conn, note_id)


# PUBLIC_INTERFACE
def delete_note(conn: sqlite3.Connection, note_id: int) -> bool:
    """Delete a note. Returns True if deleted, False if not found."""
    cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    return cur.rowcount > 0
