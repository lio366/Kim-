from locust import HttpUser, between, task


class EnterpriseUser(HttpUser):
    wait_time = between(0.05, 0.2)

    def on_start(self):
        response = self.client.post("/v1/auth/token", json={"org_id": "enterprise-load", "daily_quota": 1000000})
        token = response.json()["access_token"]
        self.headers = {"Authorization": "Bearer " + token}

    @task
    def process(self):
        self.client.post("/v1/process", json={"text": "stress payload"}, headers=self.headers)
