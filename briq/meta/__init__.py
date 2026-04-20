"""
Meta / Developer info module — Phase 1.
Covers: GET /, GET /version, GET /karibu/x-api-key
"""


class MetaAPI:
    def __init__(self, client):
        self.client = client

    def hello(self):
        """GET / — redirect to Briq landing page info."""
        return self.client.get("", prefix="", auth="none")

    def get_version(self):
        """GET /version — return API version and deployment information."""
        return self.client.get("version", prefix="", auth="none")

    def developer_stats(self):
        """GET /karibu/x-api-key — verify API key and return developer information."""
        return self.client.get("karibu/x-api-key", prefix="", auth="api_key")
