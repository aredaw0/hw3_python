from locust import HttpUser, task, between

class UrlShortenerUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def create_anon_link(self):
        self.client.post("/links/shorten", json={
            "original_url": "https://example.com/"
        })

    @task(1)
    def visit_link(self):
        for short_code in ["abc123", "test123"]:
            self.client.get(f"/{short_code}", name="/{short_code}")
