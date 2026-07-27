from fastapi.testclient import TestClient
from app.main import app
from app.api.visual_generator import compile_prompt_layers, VisualGeneratorPayload

client = TestClient(app)

def test_prompt_compilation():
    payload_data = {
        "subject": "luxury perfume bottle",
        "context": "floating over rough black volcanic rocks",
        "photo_specs": {
            "camera_body": "medium-format",
            "lens": "105mm macro",
            "aperture": "f/2.8",
            "lighting_scheme": "chiaroscuro",
            "lighting_direction": "rembrandt",
            "temp": 3200,
            "angle": "eye-level",
            "framing": "extreme-close-up"
        },
        "consistency": {
            "module_a_active": True,
            "module_a_weight": 0.85,
            "module_b_active": False,
            "module_b_weight": 0.70,
            "module_c_active": False,
            "module_c_weight": 0.60,
            "module_d_active": True,
            "module_d_weight": 0.90
        },
        "engine": "mock"
    }
    
    payload = VisualGeneratorPayload(**payload_data)
    compiled = compile_prompt_layers(payload)
    
    assert "luxury perfume bottle" in compiled
    assert "Hasselblad X2D 100C" in compiled or "Phase One" in compiled
    assert "aperture f/2.8" in compiled
    assert "3200K" in compiled

def test_draft_prompt_endpoint():
    # Test macro lens mapping for perfume
    payload_data = {
        "subject_description": "Luxury perfume glass bottle with cold water droplets",
        "aspect_ratio": "1:1"
    }
    
    response = client.post("/api/generator/draft-prompt", json=payload_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "prompt_drafted" in data
    assert "105mm macro" in data["inferred_lens"]
    assert "f/8.0" in data["inferred_aperture"]
    assert "Phase One" in data["inferred_camera"]

    payload_data_car = {
        "subject_description": "A sports red car driving at night, movie cinematic style",
        "aspect_ratio": "16:9"
    }
    response_car = client.post("/api/generator/draft-prompt", json=payload_data_car)
    assert response_car.status_code == 200
    
    data_car = response_car.json()
    assert "35mm anamorphic" in data_car["inferred_lens"]
    assert "ARRI Alexa" in data_car["inferred_camera"]

def test_generate_endpoint_mock():
    payload_data = {
        "subject": "perfume bottle",
        "context": "studio backdrop",
        "photo_specs": {
            "camera_body": "full-frame",
            "lens": "50mm",
            "aperture": "f/1.8",
            "lighting_scheme": "studio",
            "lighting_direction": "rembrandt",
            "temp": 5600,
            "angle": "eye-level",
            "framing": "close-up"
        },
        "consistency": {
            "module_a_active": False,
            "module_a_weight": 0.85,
            "module_b_active": False,
            "module_b_weight": 0.70,
            "module_c_active": False,
            "module_c_weight": 0.60,
            "module_d_active": False,
            "module_d_weight": 0.90
        },
        "engine": "mock"
    }
    
    response = client.post("/api/generator/generate", json=payload_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "photo-1523275335684" in data["image_url"] or "gen_mock_" in data["image_url"]
    assert data["engine_used"] == "mock_inteligen_local"

def test_sessions_endpoint():
    session_data = {
        "name": "Test Perfume Sauvage",
        "aspect_ratio": "1:1",
        "subject_description": "Sauvage product reference",
        "module_a_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "module_a_weight": 0.85
    }
    
    # Save session
    response_save = client.post("/api/generator/sessions/save", json=session_data)
    assert response_save.status_code == 200
    assert response_save.json()["success"] is True
    
    # List sessions
    response_list = client.get("/api/generator/sessions")
    assert response_list.status_code == 200
    
    sessions = response_list.json()
    assert len(sessions) > 0
    
    # Check if our test session is in list
    names = [s["name"] for s in sessions]
    assert "Test Perfume Sauvage" in names
