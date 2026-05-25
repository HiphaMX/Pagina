import os
from google.oauth2.credentials import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

# Diccionario de clientes y sus IDs de propiedad
CLIENTS = {
    "Botica Silvestre": "536773153",
    "Uro Oncology": "449411973",
    "White Clean": "291043945",
    "Hipha": "536740396",
    "HealthyIce": "537288803",
    "AMDI": "274628817",
    "Dr Jairo Dominguez": "274579082",
    "Centro de Urología Avanzada": "274665439",
    "DAM Pisos": "527686536",
    "El Ofertón del Piso": "527662743"
}

def get_ga4_client():
    """Inicializa y retorna el cliente de GA4 usando el token guardado."""
    secrets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.secrets')
    token_file = os.path.join(secrets_dir, 'token.json')
    client_secrets_file = os.path.join(secrets_dir, 'client_secret.json')
    
    if not os.path.exists(token_file):
        raise FileNotFoundError(f"No se encontró el token de acceso en {token_file}")

    creds = Credentials.from_authorized_user_file(token_file)
    return BetaAnalyticsDataClient(credentials=creds)

def get_basic_metrics(property_id: str, start_date: str = "30daysAgo", end_date: str = "today"):
    """Obtiene métricas básicas (nuevos usuarios, total usuarios, vistas) para un periodo dado."""
    client = get_ga4_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="newUsers"),
            Metric(name="activeUsers"),
            Metric(name="screenPageViews")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    
    try:
        response = client.run_report(request)
        
        # Procesar resultados para gráficas
        dates_data = []
        total_new_users = 0
        total_active_users = 0
        total_views = 0
        
        for row in response.rows:
            date_str = row.dimension_values[0].value
            new_u = int(row.metric_values[0].value)
            act_u = int(row.metric_values[1].value)
            views = int(row.metric_values[2].value)
            
            total_new_users += new_u
            total_active_users += act_u
            total_views += views
            
            dates_data.append({
                "date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}",
                "newUsers": new_u,
                "activeUsers": act_u,
                "views": views
            })
            
        # Ordenar por fecha
        dates_data.sort(key=lambda x: x["date"])
            
        return {
            "summary": {
                "newUsers": total_new_users,
                "activeUsers": total_active_users,
                "views": total_views
            },
            "trend": dates_data
        }
    except Exception as e:
        print(f"Error fetching data for property {property_id}: {str(e)}")
        return {"error": str(e), "summary": {"newUsers": 0, "activeUsers": 0, "views": 0}, "trend": []}

def get_top_sections(property_id: str, start_date: str = "30daysAgo", end_date: str = "today", limit: int = 10):
    """Obtiene las 10 secciones más visitadas."""
    client = get_ga4_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit
    )
    
    try:
        response = client.run_report(request)
        results = []
        for row in response.rows:
            results.append({
                "title": row.dimension_values[0].value,
                "path": row.dimension_values[1].value,
                "views": int(row.metric_values[0].value)
            })
        return results
    except Exception as e:
         print(f"Error fetching top sections for property {property_id}: {str(e)}")
         return []

def get_traffic_sources(property_id: str, start_date: str = "30daysAgo", end_date: str = "today", limit: int = 5):
    """Obtiene los orígenes de tráfico principales."""
    client = get_ga4_client()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="sessionSource")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit
    )
    
    try:
        response = client.run_report(request)
        results = []
        for row in response.rows:
            source = row.dimension_values[0].value
            if source == '(direct)':
                source = 'Directo'
            results.append({
                "source": source.capitalize(),
                "views": int(row.metric_values[0].value)
            })
        return results
    except Exception as e:
         print(f"Error fetching traffic sources for property {property_id}: {str(e)}")
         return []
