from mongo_migrate.base_migrate import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        initial_note = [
            {
                "subject": "First note",
                "description": "This is the first note"
            },
            {
                "subject": "Second note",
                "description": "This is the second note"
            }
        ]
        self.db['note'].insert_many(initial_note)
        
    def downgrade(self):
        self.db['note'].delete_many({})
        
    def comment(self):
        return 'first migration with sample data for note collection'
    