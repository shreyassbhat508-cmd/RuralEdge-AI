import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


class TestBusinessAnalyzeEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @patch("app.routes.business.get_recommendations")
    def test_01_valid_business_analyze_request(self, mock_get_recs):
        mock_get_recs.return_value = [
            {
                "scheme": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Pradhan Mantri Kisan Samman Nidhi",
                    "short_name": "PM-KISAN",
                    "ministry": "Ministry of Agriculture",
                    "description": "Financial support scheme",
                },
                "match_score": 85,
                "match_reasons": ["Location match"],
                "benefits": [],
            }
        ]

        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
                "village": "XYZ Village",
            },
            "business_category": "Dairy",
            "margin_capital": 100000,
            "project_cost": 1000000,
        }

        res = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(res.status_code, 200)

        data = res.json()

        # Verify top-level structure
        self.assertIn("business", data)
        self.assertIn("market", data)
        self.assertIn("opportunity", data)
        self.assertIn("finance", data)
        self.assertIn("scheme", data)
        self.assertIn("swot", data)

        # Verify business object
        self.assertEqual(data["business"]["category"], "Dairy")
        self.assertEqual(data["business"]["location"]["state"], "Karnataka")
        self.assertEqual(data["business"]["location"]["district"], "Kodagu")
        self.assertEqual(data["business"]["project_cost"], 1000000)
        self.assertEqual(data["business"]["margin_capital"], 100000)

        # Verify finance object
        self.assertEqual(data["finance"]["project_cost"], 1000000)
        self.assertEqual(data["finance"]["margin_contribution"], 100000)
        self.assertEqual(data["finance"]["margin_percentage"], 10.0)
        self.assertEqual(data["finance"]["loan_amount"], 900000)
        self.assertIsNotNone(data["finance"]["approx_monthly_payment"])

        # Verify market object
        self.assertEqual(data["market"]["status"], "insufficient_data")

        # Verify opportunity object
        self.assertEqual(data["opportunity"]["status"], "pending_market_analysis")
        self.assertIsNone(data["opportunity"]["score"])

        # Verify scheme object
        self.assertEqual(data["scheme"]["status"], "matched")
        self.assertIsNotNone(data["scheme"]["recommended_scheme"])
        self.assertEqual(data["scheme"]["recommended_scheme"]["name"], "Pradhan Mantri Kisan Samman Nidhi")

        # Verify swot object
        self.assertIn("strengths", data["swot"])
        self.assertIn("weaknesses", data["swot"])
        self.assertIn("opportunities", data["swot"])
        self.assertIn("threats", data["swot"])

    def test_02_margin_greater_than_project_cost(self):
        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
            },
            "business_category": "Dairy",
            "margin_capital": 1500000,
            "project_cost": 1000000,
        }
        res = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(res.status_code, 422)

        data = res.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

    def test_03_invalid_project_cost(self):
        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
            },
            "business_category": "Dairy",
            "margin_capital": 100000,
            "project_cost": 0,
        }
        res = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(res.status_code, 422)

        data = res.json()
        self.assertFalse(data.get("success", True))
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

    def test_04_missing_required_location_fields(self):
        payload = {
            "location": {
                "state": "",
                "district": "Kodagu",
            },
            "business_category": "Dairy",
            "margin_capital": 100000,
            "project_cost": 1000000,
        }
        res = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()
