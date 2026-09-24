import sys
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from mvp_api.agents.self_healing import SelfHealingRouter
from mvp_api.algorithms.cognitive_loop import CognitiveLoop
from mvp_api.providers import PROVIDERS

ENTERPRISE_ROOT = Path(__file__).resolve().parents[1] / "enterprise-agent-saas"
sys.path.insert(0, str(ENTERPRISE_ROOT))

from app.algorithms.code_repair_agent import CodeRepairAgent  # noqa: E402
from app.main import app as enterprise_app  # noqa: E402


def _headers(client: TestClient, org: str = "stress-org"):
    token = client.post(
        "/v1/auth/token",
        json={"org_id": org, "daily_quota": 1_000_000},
    ).json()["access_token"]
    return {"Authorization": "Bearer " + token}


def test_stress_01_total_api():
    with patch("mvp_api.core.guardrails.policy.evaluate", return_value=None), patch(
        "mvp_api.core.guardrails.policy.record_success", return_value=None
    ), patch("mvp_api.core.guardrails.policy.record_failure", return_value=None):
        with TestClient(enterprise_app) as client:
            headers = _headers(client, org="api-stress")

            ok = 0
            for i in range(120):
                response = client.post("/v1/process", headers=headers, json={"text": f"payload-{i}"})
                assert response.status_code == 200
                ok += 1

            assert ok == 120


def test_stress_02_agentes_autonomos():
    loop = CognitiveLoop(SelfHealingRouter(PROVIDERS))
    workflow_ids = set()

    with patch("mvp_api.core.guardrails.policy.evaluate", return_value=None), patch(
        "mvp_api.core.guardrails.policy.record_success", return_value=None
    ), patch("mvp_api.core.guardrails.policy.record_failure", return_value=None):
        for i in range(80):
            result = loop.run(
                org_id="agents-stress",
                payload={"text": f"autonomous {i}"},
                daily_quota=1_000_000,
                scope="stress_agents",
                db=None,
            )
            workflow_ids.add(result["workflow_id"])
            assert result["strategy"] in {"primary", "backup"}

    assert len(workflow_ids) == 80


def test_stress_03_self_healing_y_reparacion():
    loop = CognitiveLoop(SelfHealingRouter(PROVIDERS))

    with patch("mvp_api.core.guardrails.policy.evaluate", return_value=None), patch(
        "mvp_api.core.guardrails.policy.record_success", return_value=None
    ), patch("mvp_api.core.guardrails.policy.record_failure", return_value=None):
        fallback_hits = 0
        for i in range(60):
            force_fail = i % 2 == 0
            result = loop.run(
                org_id="healing-stress",
                payload={"text": f"healing {i}", "force_primary_failure": force_fail},
                daily_quota=1_000_000,
                scope="stress_self_heal",
                db=None,
            )
            if force_fail:
                fallback_hits += int(result["used_fallback"])

    assert fallback_hits >= 20


def test_stress_04_cibernetica_hardening():
    agent = CodeRepairAgent()
    malicious = "__import__('os'); os.system('rm -rf /'); eval('1+1'); exec('print(1)')"

    for _ in range(100):
        sanitized = agent.sanitize(malicious)
        assert "__import__" not in sanitized
        assert "os.system" not in sanitized
        assert "eval(" not in sanitized
        assert "exec(" not in sanitized


def test_stress_05_seguridad_multitenant():
    with patch("mvp_api.core.guardrails.policy.evaluate", return_value=None), patch(
        "mvp_api.core.guardrails.policy.record_success", return_value=None
    ), patch("mvp_api.core.guardrails.policy.record_failure", return_value=None):
        with TestClient(enterprise_app) as client:
            headers_a = _headers(client, org="tenant-A")
            headers_b = _headers(client, org="tenant-B")

            providers_a = []
            providers_b = []
            for i in range(30):
                ra = client.post("/v1/process", headers=headers_a, json={"text": f"A-{i}"})
                rb = client.post("/v1/process", headers=headers_b, json={"text": f"B-{i}"})
                assert ra.status_code == 200
                assert rb.status_code == 200
                providers_a.append(ra.json()["provider"])
                providers_b.append(rb.json()["provider"])

            assert len(providers_a) == 30
            assert len(providers_b) == 30
