import json
import os
import pytest


def test_vercel_json_validity():
    """Verify that vercel.json exists and is a valid JSON file."""
    vercel_path = "vercel.json"
    assert os.path.exists(vercel_path), "vercel.json is missing!"
    
    with open(vercel_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"vercel.json is not a valid JSON: {str(e)}")
            
    # Basic structural checks
    assert "routes" in data, "routes key is missing from vercel.json"
    assert isinstance(data["routes"], list), "routes must be a list"


def test_vercel_routes_destination_exists():
    """Verify that all project directories targeted in vercel.json routes actually exist in the repository."""
    vercel_path = "vercel.json"
    with open(vercel_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # We extract all destinations containing '/projects/' and verify they map to actual folders
    for route in data.get("routes", []):
        dest = route.get("dest")
        if dest and "/projects/" in dest:
            # Clean dest path to find the base directory under projects/
            # E.g., "/projects/urologia-avanzada/$1" -> "projects/urologia-avanzada"
            # E.g., "/projects/AMDI/index.html" -> "projects/AMDI"
            parts = dest.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "projects":
                project_dir = os.path.join("projects", parts[1])
                assert os.path.exists(project_dir), f"Target directory '{project_dir}' for routing '{dest}' does not exist!"
                assert os.path.isdir(project_dir), f"'{project_dir}' must be a directory!"


def test_api_entrypoint_exists():
    """Verify that the Vercel API entrypoint index.py exists and correctly references the app."""
    entrypoint_path = "api/index.py"
    assert os.path.exists(entrypoint_path), "api/index.py is missing!"
    
    with open(entrypoint_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "from app.main import app" in content, "api/index.py does not correctly import app"


def test_fastapi_app_importable():
    """Verify that the FastAPI application is importable and has core configurations in order."""
    try:
        from app.main import app
        assert app.title == "HiphaMX API"
    except ImportError as e:
        pytest.fail(f"Failed to import app.main: {str(e)}")
