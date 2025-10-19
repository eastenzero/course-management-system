# Course Management System — Project Structure & Windows Compatibility

This repository uses a flattened structure with a Linux-friendly compatibility symlink. This document explains the layout and how to run the system on Windows without relying on symlinks.

## Project structure
- `app/`
  - Main project root (backend, frontend, scripts, docs)
  - Example paths:
    - Backend: `app/backend/`
    - Frontend: `app/frontend/`
    - Algorithms data: `app/algorithms/`
    - Data generation docs: `app/backend/data_generation/`
- `course-management-system` (symlink)
  - Linux/macOS convenience symlink pointing to `app/`
  - Not required on Windows. Windows users can use `app/` directly.
- `archive/legacy_backend_root/backend/`
  - Archived legacy root-level backend (kept for reference only)
- `results/`, `docs/`
  - Auxiliary materials and scripts

## What changed (compatibility improvements)
- Scripts that previously used absolute paths now resolve paths relative to their script directory:
  - `app/cors_data_server.py`
  - `app/backend/import_schedule_standalone.py`
  - `app/backend/import_schedule_results.py`
  - `app/start_complete_system.sh`
- These changes improve portability across Linux/macOS/Windows.

## Windows notes
- The Linux symlink `course-management-system -> app` may not work on Windows in some environments (without elevated privileges or special git settings). On Windows, prefer using the real path `app/`.
- If you strictly need the old path, you can create a directory junction (run as Administrator):
  - Command Prompt:
    ```bat
    mklink /J course-management-system app
    ```
  - PowerShell (as Admin):
    ```powershell
    New-Item -ItemType Junction -Path "course-management-system" -Target "app"
    ```

## Running on Windows (recommended)
- Prerequisites:
  - Node.js (LTS), npm
  - Python 3.10+ (with `py` launcher or `python` available)

- Start data server (serves static data to avoid CORS issues):
  ```powershell
  # from repo root
  Set-Location app/frontend/public
  py -3 -m http.server 8080
  # or: python -m http.server 8080
  ```

- Start frontend (new terminal):
  ```powershell
  # from repo root
  Set-Location app/frontend
  $env:VITE_USE_MOCK_API = "true"
  $env:VITE_DATA_SERVER_URL = "http://localhost:8080"
  npm install
  npm run dev -- --host 0.0.0.0 --port 3001
  ```

- Optional: use the CORS data server script (resolves paths automatically):
  ```powershell
  # from repo root
  Set-Location app
  py -3 cors_data_server.py
  # Access http://localhost:8080/data/schedules.json
  ```

- Optional: one-click startup (PowerShell script):
  ```powershell
  # from repo root
  Set-Location app
  .\start_complete_system.ps1
  # This will start:
  # - Data server on 8080 serving app/frontend/public
  # - Frontend dev server on 3001 using mock API and data server
  ```

## Importing algorithm results (optional)
- Standalone conversion (no Django): `app/backend/import_schedule_standalone.py`
  - Reads: `app/algorithms/genetic_scheduling_result.json`
  - Writes: `app/frontend/public/data/schedules.json`

- Import into Django DB (requires Django environment): `app/backend/import_schedule_results.py`
  - Now uses relative paths; ensure your virtual environment and Django settings are active.

## Git symlink and Windows
- If you clone on Windows and want symlinks preserved, ensure developer mode is enabled or run git with symlink support. Otherwise, use the real `app/` folder.
- Git setting (optional):
  ```bat
  git config core.symlinks true
  ```

## Troubleshooting
- If files are not found, verify you’re using the `app/` path on Windows.
- Ensure `app/frontend/public/data/schedules.json` exists when testing the frontend schedule pages.

## Security note
- Avoid committing credentials (tokens, PATs) into the repository. Prefer environment variables or local credential managers.
