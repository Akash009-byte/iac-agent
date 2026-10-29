# Validation

10 HTTP integration checks passed on Python 3.12 with local test storage. Tests use isolated test database names and no cloud credentials.


Checks:

- OpenAPI
- Readiness
- Homepage
- UI metadata
- Webapp route
- Create note
- Read note
- Delete note
- Invalid note ID handled
- Integration status

Run again after installing requirements.lock.txt:

```sh
.venv/bin/python tests/smoke.py
```

Mongo projects require a local MongoDB server (default port 27017; override TEST_MONGO_PORT for tests). Keep the backend stopped on port 18510 before testing. Live OpenAI, AWS, Discord and Google Sheets integrations require valid credentials and remain unverified.
