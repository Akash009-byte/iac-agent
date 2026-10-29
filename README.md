# AgentOps / IaC Agent

A FastAPI web interface for infrastructure-agent conversations, activity logs and AWS EC2 operations. Adapted from [raxkumar/iac-agent](https://github.com/raxkumar/iac-agent).

## Local start

Requires Python 3.12 and Node.js 22+.

```sh
python3.12 dev.py
```

See [RUN_LOCALLY.md](RUN_LOCALLY.md) for storage, configuration and port details. The launcher uses isolated dependencies and persistent local data.

## Verification

[VALIDATION.md](VALIDATION.md) lists the passing integration tests and how to rerun them.

## External services

Supply your own credentials in `app/.env` for the integrations you enable. Cloud integrations have not been validated against live accounts. The launcher binds to localhost for development; public deployment requires authentication, authorization and an appropriate deployment configuration.

Legacy credentials were removed from current source. Their owners must revoke exposed keys because earlier Git history and upstream copies can still contain them.

[Original project notes and attribution](docs/original-project-notes.md).
