import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

VALID_SCHEME_ID = "b259d19f-fc94-4be2-90bd-3d27be2b8eec"
NONEXISTENT_SCHEME_ID = "00000000-0000-0000-0000-000000000000"
INVALID_UUID = "not-a-valid-uuid-string"


class TestFullBackendIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # --- 1. Health API ---
    def test_01_get_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "RuralEdge Backend")
        self.assertIn("database", data)

    # --- 2. Schemes API ---
    def test_02_get_schemes(self):
        res = self.client.get("/api/schemes?page=1&limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total", data)

    def test_03_get_schemes_search(self):
        res = self.client.get("/api/schemes/search?query=Janani")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_04_get_scheme_by_id_valid(self):
        res = self.client.get(f"/api/schemes/{VALID_SCHEME_ID}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], VALID_SCHEME_ID)

    def test_05_get_scheme_by_id_nonexistent(self):
        res = self.client.get(f"/api/schemes/{NONEXISTENT_SCHEME_ID}")
        self.assertEqual(res.status_code, 404)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "SCHEME_NOT_FOUND")

    def test_06_get_scheme_by_id_invalid_uuid(self):
        res = self.client.get(f"/api/schemes/{INVALID_UUID}")
        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

    def test_07_get_scheme_details(self):
        res = self.client.get(f"/api/schemes/{VALID_SCHEME_ID}/details")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("scheme", data)
        self.assertIn("eligibility", data)
        self.assertIn("benefits", data)

    # --- 3. Eligibility & Benefits APIs ---
    def test_08_get_scheme_eligibility(self):
        res = self.client.get(f"/api/schemes/{VALID_SCHEME_ID}/eligibility")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_09_get_scheme_benefits(self):
        res = self.client.get(f"/api/schemes/{VALID_SCHEME_ID}/benefits")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_10_post_eligibility_check_valid(self):
        res = self.client.post(
            f"/api/schemes/{VALID_SCHEME_ID}/eligibility-check",
            json={"state": "Karnataka", "gender": "female", "occupation": "pregnant women"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("eligible", data)
        self.assertIn("reasons", data)

    def test_11_post_eligibility_check_nonexistent(self):
        res = self.client.post(
            f"/api/schemes/{NONEXISTENT_SCHEME_ID}/eligibility-check",
            json={"gender": "female"},
        )
        self.assertEqual(res.status_code, 404)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "SCHEME_NOT_FOUND")

    # --- 4. Recommendations API ---
    def test_12_post_recommendations_valid(self):
        res = self.client.post(
            "/api/recommendations",
            json={"state": "Karnataka", "gender": "female", "occupation": "pregnant women"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("match_score", data[0])
            self.assertIn("match_reasons", data[0])
            self.assertIn("warnings", data[0])

    def test_13_post_recommendations_empty(self):
        res = self.client.post("/api/recommendations", json={})
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    # --- 5. Loan Calculator APIs ---
    def test_14_post_loan_calculator_valid(self):
        res = self.client.post(
            "/api/loan-calculator",
            json={
                "project_cost": 1000000.0,
                "margin_percentage": 10.0,
                "annual_interest_rate": 6.0,
                "repayment_period_months": 60,
                "moratorium_months": 6,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["project_cost"], 1000000.0)
        self.assertEqual(data["margin_amount"], 100000.0)
        self.assertEqual(data["loan_amount"], 900000.0)

    def test_15_post_loan_calculator_invalid_input(self):
        res = self.client.post(
            "/api/loan-calculator",
            json={
                "project_cost": -500.0,  # Invalid negative cost
                "margin_percentage": 10.0,
            },
        )
        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

    def test_16_post_loan_calculator_scheme_valid(self):
        res = self.client.post(
            f"/api/loan-calculator/scheme/{VALID_SCHEME_ID}",
            json={"project_cost": 500000.0, "margin_percentage": 10.0},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["project_cost"], 500000.0)

    # --- 6. Reference APIs ---
    def test_17_get_locations(self):
        res = self.client.get("/api/locations")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_18_get_sources(self):
        res = self.client.get("/api/sources")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_19_get_ingestion(self):
        res = self.client.get("/api/ingestion")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    def test_20_get_documents(self):
        res = self.client.get("/api/documents")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)

    # --- 7. AI Assistant API ---
    @patch("app.services.ai_service.httpx.Client")
    def test_21_post_ai_chat_valid(self, mock_httpx):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Janani Suraksha Yojana provides financial aid to eligible pregnant women."
                            }
                        ]
                    }
                }
            ]
        }
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_instance

        with patch.dict(os.environ, {"GEMINI_API_KEY": "mock_api_key"}):
            res = self.client.post(
                "/api/ai/chat",
                json={
                    "message": "Explain this scheme",
                    "scheme_id": VALID_SCHEME_ID,
                },
            )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("Janani Suraksha Yojana", data["reply"])

    def test_22_post_ai_chat_failure_503(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            res = self.client.post("/api/ai/chat", json={"message": "Test question"})
        self.assertEqual(res.status_code, 503)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "AI_SERVICE_UNAVAILABLE")

    # --- 8. OpenAPI & Docs ---
    def test_23_get_openapi_json(self):
        res = self.client.get("/openapi.json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("paths", data)

    def test_24_get_docs(self):
        res = self.client.get("/docs")
        self.assertEqual(res.status_code, 200)

    # --- 9. CORS Verification ---
    def test_25_cors_allowed_origin_3000(self):
        res = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(res.headers.get("access-control-allow-origin"), "http://localhost:3000")

    def test_26_cors_allowed_origin_5173(self):
        res = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(res.headers.get("access-control-allow-origin"), "http://localhost:5173")

    def test_27_cors_unauthorized_origin(self):
        res = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://unauthorized-malicious-domain.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertNotEqual(
            res.headers.get("access-control-allow-origin"),
            "http://unauthorized-malicious-domain.com",
        )


if __name__ == "__main__":
    unittest.main()
