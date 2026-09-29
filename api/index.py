import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI(title="HiphaMX API (Emergency Fallback)")
    error_trace = traceback.format_exc()
    print("FATAL IMPORT ERROR:", error_trace)

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    def emergency_catch_all(path_name: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend function failed to initialize",
                "detail": str(e),
                "traceback": error_trace
            }
        )

