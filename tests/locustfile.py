from locust import HttpUser, between, task


class KimiUser(HttpUser):
    wait_time = between(0.05, 0.2)

    def on_start(self):
        response = self.client.post(
            "/v1/auth/token",
            json={"org_id": "locust-org", "daily_quota": 1000000},
            name="auth_token",
        )
        token = response.json()["access_token"]
        self.headers = {"Authorization": "Bearer " + token}

    @task(3)
    def process_sync(self):
        self.client.post(
            "/v1/process",
            json={"text": "hola kim"},
            headers=self.headers,
            name="process_sync",
        )

    @task(1)
    def process_async(self):
        self.client.post(
            "/v1/process/async",
            json={"text": "hola kim"},
            headers=self.headers,
            name="process_async",
        )
