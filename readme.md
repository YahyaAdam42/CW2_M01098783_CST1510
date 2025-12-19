# Cybersecurity Intelligence Platform (Tier 3)

This repository contains a Streamlit-based cybersecurity intelligence platform, dataset migration scripts, and helper modules.

Contents:

- `attempts.py` — Streamlit app (main UI and chat integration)
- `test.py` — Database creation & CSV migration helper
- `log_hash.py` — Password hashing and user management helpers
- `app/` — small modules for datasets, users, tickets
- `DATA/` — CSVs and generated SQLite DB (database files are gitignored)

Note: `.streamlit/secrets.toml` contains an OpenAI key and is excluded from this repository. Create your own secrets file before running the app.
description to be confirmed...