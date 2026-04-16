# Laser Settings Vault

A full-stack, mobile-first web application designed for makers (woodworking and laser engraving professionals) to log, structure, and systematically test their material laser settings.

---

## 🏗️ Architecture & Tech Stack

This project is built using a modern, lightweight, and robust stack suitable for self-hosting and quick scaffolding:

### Backend
* **Python (FastAPI)**: Provides high-performance, asynchronous REST API endpoints.
* **Database (SQLite + SQLAlchemy)**: A lightweight local relational database structured using an ORM for maintainability.
* **Migrations (Alembic)**: Robust database migration logic. If models change, Alembic ensures existing data is kept safe while altering the schema.

### Frontend
* **UI Structure**: Served directly as statically hosted files (`index.html`) using FastAPI's standard `.mount()` mechanisms.
* **Styling (Tailwind CSS via CDN)**: Used for responsive layout, dark/light modes, floating elements, glass-matching features, and overall aesthetic.
* **Reactivity (Alpine.js)**: Handles all DOM manipulation, fetch requests, UI state, and modal management without needing a heavy compilation step (like React/Vue). No Node.js build process is required.

---

## 📁 Folder Structure

To help other AI agents or developers navigate the codebase, here is a detailed breakdown of the files:

```text
.
├── main.py                # Core application entrypoint. Defines the FastAPI app, API routes, and static file mounts.
├── database.py            # Sets up the SQLAlchemy Engine, SQLite URL (laser_vault.db), and SessionLocal context manager.
├── models.py              # Contains the declarative SQLAlchemy models (e.g., EntryLog). DB schema is defined here.
├── schemas.py             # Contains Pydantic models mapping incoming HTTP request bodies and serializing outgoing responses.
├── alembic.ini            # Primary configuration file for Alembic database migrations. Points to the local SQLite DB.
├── migrations/            # The directory housing your migration scripts.
│   ├── env.py             # Modified to import `models.Base.metadata` so Alembic can autogenerate migrations.
│   └── versions/          # Individual python scripts tracking incremental schema changes via revision hashes.
├── static/                # Hosted via FastAPI at `/static` and handles all frontend interactions.
│   └── index.html         # The complete Alpine.js + Tailwind HTML file serving the user interface.
├── uploads/               # Created dynamically if it doesn't exist. Used to locally host the user-uploaded reference images.
├── laser_vault.db         # The auto-generated SQLite database containing the application payload.
├── requirements.txt       # Python dependency freeze map.
├── Dockerfile             # Standard Python-slim containerization instructions.
└── docker-compose.yml     # Compose file mapping the active directory as a volume for real-time development.
```

---

## 🤖 Guide for AI Agents & vibecoding

If you are an AI assistant updating or extending this codebase, please adhere to the following rules:

### 1. Database & Schema Changes
If the user requests a new feature that requires a database change (e.g., adding a "Material Thickness" column):
1. **Never** manually delete `laser_vault.db`.
2. Update the columns inside `models.py`.
3. Update the matching Pydantic response models and payloads inside `schemas.py`.
4. Run the following commands to securely generate and apply the migrations:
   ```bash
   alembic revision --autogenerate -m "Added Material Thickness"
   alembic upgrade head
   ```
5. Update `main.py` entrypoint creation logic if new parameters are injected into the payload.

### 2. Frontend Modifications
The entire frontend lives inside `static/index.html`.
* The state is managed under the `<div x-data="app()">` container using Alpine.js.
* Core data objects (like `entries` and `formData`) exist within the `<script>` tag at the bottom.
* If making form changes, remember to update the `resetForm()` bind mappings so the "Quick-Clone" and "Add New" states clear correctly.
* The API logic handles images purely through `FormData`. Ensure any new input states are successfully injected into the standard `fd.append()` map.

### 3. Running the App (Docker)
A `docker-compose.yml` file is provided that mounts the root directory into the container's `/app` folder as a live volume. 

To start the project natively using Docker with hot-reloading:
```bash
docker compose up --build
```
* **Ports**: Exposes `8000` to `8000`.
* **Volumes**: The host folder is fully mapped, meaning the database `.db` file and the `uploads/` directory persist naturally on the host system without complicated named volumes. Modifications to standard `.py` files inside the container will auto-reload thanks to the `--reload` flags on the compose file.
