Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'e:\pythonas\plat\backend'; uv run uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'e:\pythonas\plat\frontend'; pnpm dev"
