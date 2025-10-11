from fastapi import APIRouter, HTTPException, Depends
from services.note_service import NoteService
from models.note import Note
from typing import List
from core.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix='/api'
)

# Dependency to provide a NoteService instance with MongoDB injection
def get_note_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> NoteService:
    return NoteService(db=db)

@router.post("/notes", response_model=Note)
async def create_note(note: Note, notes_service: NoteService = Depends(get_note_service)):
    return await notes_service.create_note(
        subject=note.subject, description=note.description
    )

@router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str, notes_service: NoteService = Depends(get_note_service)):
    note = await notes_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.get("/notes", response_model=List[Note])
async def get_all_notes(notes_service: NoteService = Depends(get_note_service)):
    return await notes_service.get_all_notes()

@router.delete("/notes/{note_id}")
async def delete_note(note_id: str, notes_service: NoteService = Depends(get_note_service)):
    success = await notes_service.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}
