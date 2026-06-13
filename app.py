"""
HuggingFace Spaces Entry Point.
Runs the FastAPI app on port 7860 as required by HF Spaces.
"""

import uvicorn
from api import app

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=7860, reload=False)
