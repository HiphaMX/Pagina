import httpx
from app.core.config import settings

class WebflowClient:
    def __init__(self):
        self.api_token = settings.WEBFLOW_API_TOKEN
        self.site_id = settings.WEBFLOW_SITE_ID
        self.base_url = "https://api.webflow.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "accept-version": "1.0.0",
            "Content-Type": "application/json"
        }

    async def get_collections(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/sites/{self.site_id}/collections",
                headers=self.headers
            )
            resp.raise_for_status()
            return resp.json()

    async def create_item(self, collection_id: str, field_data: dict, is_draft: bool = False):
        payload = {
            "isArchived": False,
            "isDraft": is_draft,
            "fieldData": field_data
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/collections/{collection_id}/items",
                headers=self.headers,
                json=payload
            )
            resp.raise_for_status()
            return resp.json()

webflow_client = WebflowClient()
