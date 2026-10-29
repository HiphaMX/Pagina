from app.services.analytics import get_top_sections
from unittest.mock import MagicMock, patch

def test_top_sections_consolidation():
    mock_row1 = MagicMock()
    mock_row1.dimension_values = [MagicMock(value="/salsa-de-arbol"), MagicMock(value="Salsa Chile de Árbol Artesanal $35")]
    mock_row1.metric_values = [MagicMock(value="26")]

    mock_row2 = MagicMock()
    mock_row2.dimension_values = [MagicMock(value="/salsa-de-arbol"), MagicMock(value="Salsa Chile de Árbol $40")]
    mock_row2.metric_values = [MagicMock(value="15")]

    mock_row3 = MagicMock()
    mock_row3.dimension_values = [MagicMock(value="/semillas-enchiladas/"), MagicMock(value="Semillas Enchiladas Crujientes $60")]
    mock_row3.metric_values = [MagicMock(value="16")]

    mock_row4 = MagicMock()
    mock_row4.dimension_values = [MagicMock(value="/semillas-enchiladas"), MagicMock(value="Semillas Enchiladas Crujientes $65")]
    mock_row4.metric_values = [MagicMock(value="13")]

    mock_response = MagicMock()
    mock_response.rows = [mock_row1, mock_row2, mock_row3, mock_row4]

    mock_client = MagicMock()
    mock_client.run_report.return_value = mock_response

    with patch("app.services.analytics.get_ga4_client", return_value=mock_client):
        results = get_top_sections("dummy_prop_id", limit=10)

    assert len(results) == 2
    assert results[0]["path"] == "/salsa-de-arbol"
    assert results[0]["views"] == 41
    assert results[1]["path"] == "/semillas-enchiladas"
    assert results[1]["views"] == 29
