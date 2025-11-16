import uvicorn
from .api import app
from .config import BACKEND_HOST, BACKEND_PORT

if __name__ == "__main__":
    uvicorn.run("backend.app.api:app", host=BACKEND_HOST, port=BACKEND_PORT, log_level="info")

