# Course Management System (CMS)

A comprehensive course management system built with Django (Backend) and React (Frontend), featuring intelligent scheduling algorithms and a modern user interface.

## 📸 Screenshots
| **Dashboard** | **Course List** |
|:---:|:---:|
| ![Home](screenshots/home.png) | ![Courses](screenshots/course-list.png) |
| **Course Detail** | **Admin Panel** |
| ![Detail](screenshots/course-detail.png) | ![Admin](screenshots/admin.png) |

## 🚀 One-Click Start (Recommended)
**Prerequisites**: [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

1.  **Configure Environment**:
    ```bash
    cp .env.example .env
    # Edit .env if needed (defaults work for local dev)
    ```

2.  **Start Services**:
    ```bash
    docker-compose up -d --build
    ```

3.  **Access Application**:
    - **Frontend**: [http://localhost:15178](http://localhost:15178)
    - **Backend API**: [http://localhost:18086/api/](http://localhost:18086/api/)
    - **Admin Panel**: [http://localhost:18086/admin/](http://localhost:18086/admin/)

4.  **Stop Services**:
    ```bash
    docker-compose down
    ```

## 🏗 Project Structure
```
.
├── app/
│   ├── backend/          # Django API & Business Logic
│   ├── frontend/         # React + Vite Frontend
│   └── algorithms/       # Scheduling Algorithms
├── screenshots/          # Application Previews
├── docker-compose.yml    # Main Docker orchestration
├── .env.example          # Environment variables template
└── README.md             # This file
```

## ⚙️ Environment Variables
Check `.env.example` for the full list. Key variables include:
- `DB_PASSWORD`: Database password.
- `SECRET_KEY`: Django secret key.
- `VITE_API_BASE_URL`: Frontend API target (default: `http://localhost:18086/api/v1`).
- `FRONTEND_PORT`: Port for the web interface (default: 15178).

## ❓ FAQ
**Q: The frontend build fails with type errors?**
A: The strict type checking has been relaxed in `tsconfig.json` to allow building legacy code. Ensure you are using the provided `docker-compose` setup which handles the build environment.

**Q: I cannot connect to the database locally.**
A: Ensure your local `.env` matches your local Postgres setup. If using Docker, use the port `15432` to connect tools like DBeaver.

**Q: Container shows "unhealthy"?**
A: Check logs with `docker-compose logs -f backend`. The backend may take a moment to wait for the database.

## 🛠 Local Development (Manual & Experimental)
> **WARNING**: Local setup without Docker is **FRAGILE** due to strict dependency requirements (Python 3.9, Node 18, PostgreSQL 13, Redis 6). Use Docker whenever possible.

### Backend
1.  Navigate to `app/backend`.
2.  Create virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  Set up `.env` in `app/` (see `app/.env.example`).
4.  Run migrations and start server:
    ```bash
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
    ```

### Frontend
1.  Navigate to `app/frontend`.
2.  Install dependencies:
    ```bash
    npm install
    # Note: package.json has been recreated; verify dependencies if issues arise.
    ```
3.  Start dev server:
    ```bash
    npm run dev
    ```
