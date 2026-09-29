import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="HiphaMX Emergency Fallback")
    err_trace = traceback.format_exc()
    print("FATAL STARTUP ERROR IN APP.MAIN:", err_trace)

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def emergency_catch_all(path_name: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "FastAPI App Failed to Initialize on Cold Start",
                "detail": str(e),
                "traceback": err_trace
            }
        )

