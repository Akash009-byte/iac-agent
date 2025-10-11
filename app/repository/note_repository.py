from bson import ObjectId
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

class NoteRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection("note")

    async def create_note(self, note_data: dict) -> dict:
        """Create a new note in the database."""
        result = await self.collection.insert_one(note_data)
        note_data["_id"] = str(result.inserted_id)
        return note_data

    async def get_note(self, note_id: str) -> Optional[dict]:
        """Retrieve a note by ID."""
        note = await self.collection.find_one({"_id": ObjectId(note_id)})
        if note:
            note["_id"] = str(note["_id"])
        return note

    async def get_all_notes(self) -> List[dict]:
        """Retrieve all notes."""
        notes = await self.collection.find().to_list(None)
        for note in notes:
            note["_id"] = str(note["_id"])
        return notes

    async def update_note(self, note_id: str, note_data: dict) -> bool:
        """Update an existing note."""
        result = await self.collection.update_one(
            {"_id": ObjectId(note_id)}, {"$set": note_data}
        )
        return result.modified_count > 0

    async def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        result = await self.collection.delete_one({"_id": ObjectId(note_id)})
        return result.deleted_count > 0
