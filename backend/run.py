import sys
from pathlib import Path

# Add backend directory to sys.path so 'app' module is directly importable
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"============================================================")
    print(f"🚀 Starting {settings.PROJECT_NAME} Backend Server")
    print(f"📡 API Root: http://localhost:{settings.PORT}{settings.API_V1_STR}")
    print(f"📖 Swagger Docs: http://localhost:{settings.PORT}/docs")
    print(f"============================================================")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
