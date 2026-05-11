"""
Backend entry point: imports and runs the refactored FastAPI app.
This file serves as the main entrypoint that start_backend.py calls.
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import BACKEND_HOST, BACKEND_PORT

    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT)
