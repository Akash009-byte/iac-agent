from models.note import Note
from repository.note_repository import NoteRepository
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

class NoteService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.note_repository = NoteRepository(db)

    async def create_note(self, subject: str, description: str) -> dict:
        note_data = {"subject": subject, "description": description}
        return await self.note_repository.create_note(note_data)

    async def get_note(self, note_id: str) -> Optional[dict]:
        return await self.note_repository.get_note(note_id)

    async def get_all_notes(self) -> List[dict]:
        return await self.note_repository.get_all_notes()

    async def update_note(self, note_id: str, subject: str, description: str) -> bool:
        note_data = {"subject": subject, "description": description}
        return await self.note_repository.update_note(note_id, note_data)

    async def delete_note(self, note_id: str) -> bool:
        return await self.note_repository.delete_note(note_id)
