import os
import json
import re

def test_amdi_preview_files_exist():
    assert os.path.exists("projects/AMDI-preview/index.html")
    assert os.path.exists("projects/AMDI-preview/proyectos.html")
    assert os.path.exists("projects/AMDI-preview/css/amdi-editorial.css")
    assert os.path.exists("projects/AMDI-preview/js/amdi-preview.js")

def test_amdi_preview_index_editorial_structure():
    with open("projects/AMDI-preview/index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Editorial Theme & Banner
    assert "amdi-editorial-theme" in content
    assert "amdi-preview-banner" in content
    assert "AMDI PREVIEW STAGING" in content
    
    # Header Chrome with Studio Clock
    assert "amdi-chrome" in content
    assert "amdi-clock-pill" in content
    
    # Hero Editorial
    assert "amdi-hero-editorial" in content
    assert "Espacios que trascienden la tendencia" in content
    
    # Interactive Preview Strip (Estudio Bang)
    assert "amdi-preview-strip-section" in content
    assert "amdi-strip-container" in content
    assert "Residencia Antares" in content
    assert "Residencia Jesús María" in content
    assert "Expo Obra Blanca" in content
    assert "Residencia Los Frailes" in content
    
    # Curated Asymmetric Showcase with Materials
    assert "amdi-curated-section" in content
    assert "amdi-material-chips" in content
    assert "Roble Blanco" in content
    assert "Travertino Veracruz" in content

    # Methodology & Manifesto
    assert "amdi-method-section" in content
    assert "amdi-manifesto-quote" in content
    assert "Le Corbusier" in content

    # Retained functional elements & scripts
    assert "wf-form-Newsletter-AMDI" in content
    assert "form-handler.js" in content
    assert "amdi-preview.js" in content

def test_amdi_preview_proyectos_moodboard_structure():
    with open("projects/AMDI-preview/proyectos.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Filters Bar
    assert "amdi-filters-bar" in content
    assert 'data-filter="all"' in content
    assert 'data-filter="residencial"' in content
    assert 'data-filter="comercial"' in content

    # Mosaic & Moodboard Grid
    assert "amdi-mosaic-container" in content
    assert "amdi-mosaic-card" in content
    assert "amdi-moodboard-complement" in content

    # Contains all 21 project cards
    cards = re.findall(r'class=\"[^\"]*amdi-mosaic-card[^\"]*\"', content)
    assert len(cards) == 21, f"Expected 21 project cards in moodboard, found {len(cards)}"

    # Material swatches present
    assert "amdi-swatch-dot" in content
    assert "amdi-mosaic-swatches" in content

    # Script included
    assert "amdi-preview.js" in content

def test_amdi_production_unmodified():
    # Production AMDI directory index.html must NOT have preview classes
    with open("projects/AMDI/index.html", "r", encoding="utf-8") as f:
        prod_index = f.read()
    assert "amdi-editorial-theme" not in prod_index
    assert "amdi-preview-banner" not in prod_index
    assert "amdi-preview.js" not in prod_index

    # Production AMDI proyectos.html must NOT have preview classes
    with open("projects/AMDI/proyectos.html", "r", encoding="utf-8") as f:
        prod_proyectos = f.read()
    assert "amdi-mosaic-container" not in prod_proyectos
    assert "amdi-preview-banner" not in prod_proyectos

def test_vercel_routes_include_amdi_preview():
    with open("vercel.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check ignoreCommand includes AMDI-preview
    assert "AMDI-preview" in data["ignoreCommand"]

    # Check routes
    routes = data.get("routes", [])
    preview_routes = [r for r in routes if "amdi-preview" in r.get("src", "")]
    assert len(preview_routes) >= 3
