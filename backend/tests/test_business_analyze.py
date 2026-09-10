import os
import unittest
from unittest.mock import patch, MagicMock

# Set fallback dummy environment variables for tests if not present
if "SUPABASE_URL" not in os.environ:
    os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
if "SUPABASE_KEY" not in os.environ:
    os.environ["SUPABASE_KEY"] = "mock-key-12345"

from fastapi.testclient import TestClient
from app.main import app


class TestBusinessAnalyzeAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_analyze_business_success(self):
        """Test happy path with valid inputs."""
        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
                "village": "Madikeri"
            },
            "business_category": "Dairy",
            "margin_capital": 100000,
            "project_cost": 1000000
        }
        
        # Mock get_recommendations to make test independent of live Supabase connection
        mock_recommendations = [
            {
                "scheme": {
                    "id": "mock-scheme-id",
                    "scheme_name": "Dairy Entrepreneurship Development Scheme",
                    "short_name": "DEDS",
                    "description": "Scheme for dairy sector setup",
                    "category": "Agriculture",
                    "sponsor_type": "central",
                    "state": "Karnataka",
                    "target_audience": "Farmers, Entrepreneurs",
                    "is_active": True
                },
                "match_score": 85,
                "match_reasons": ["State match: Karnataka", "Category match"],
                "eligibility": [],
                "benefits": []
            }
        ]

        with patch("app.services.business_analysis_service.get_recommendations", return_value=mock_recommendations):
            response = self.client.post("/api/business/analyze", json=payload)
            self.assertEqual(response.status_code, 200)

            data = response.json()

            # 1. Check business section
            self.assertEqual(data["business"]["category"], "Dairy")
            self.assertEqual(data["business"]["location"]["state"], "Karnataka")
            self.assertEqual(data["business"]["location"]["district"], "Kodagu")
            self.assertEqual(data["business"]["location"]["village"], "Madikeri")

            # 2. Check market section
            self.assertIn(data["market"]["status"], ["success", "no_results", "unavailable", "pending", "error"])
            self.assertEqual(data["market"]["radius_km"], 10)

            # 3. Check opportunity section
            self.assertGreater(data["opportunity"]["score"], 0)
            self.assertIn(data["opportunity"]["level"], ["Medium", "High"])
            components = data["opportunity"]["components"]
            self.assertIn("market", components)
            self.assertIn("competition", components)
            self.assertIn("financial", components)
            self.assertIn("location", components)
            self.assertIn("affordability", components)

            # 4. Check finance section
            self.assertEqual(data["finance"]["project_cost"], 1000000)
            self.assertEqual(data["finance"]["own_contribution"], 100000)
            self.assertEqual(data["finance"]["loan_amount"], 900000)
            self.assertGreater(data["finance"]["emi"], 0)
            self.assertGreater(data["finance"]["total_interest"], 0)
            self.assertGreater(data["finance"]["payback_months"], 0)

            # 5. Check scheme section
            self.assertEqual(data["scheme"]["status"], "matched")
            self.assertIsNotNone(data["scheme"]["recommended_scheme"])
            self.assertEqual(data["scheme"]["match_score"], 85)

            # 6. Check swot section
            self.assertIn("strengths", data["swot"])
            self.assertIn("weaknesses", data["swot"])
            self.assertIn("opportunities", data["swot"])
            self.assertIn("threats", data["swot"])
            self.assertTrue(len(data["swot"]["strengths"]) > 0)

    def test_02_analyze_business_margin_greater_than_project_cost(self):
        """Test validation error when margin capital exceeds project cost."""
        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
                "village": "Madikeri"
            },
            "business_category": "Dairy",
            "margin_capital": 1500000,
            "project_cost": 1000000
        }
        
        response = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("margin_capital", data["error"]["message"].lower())

    def test_03_analyze_business_equal_margin_and_project_cost(self):
        """Test zero loan amount scenario when margin capital equals project cost."""
        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
                "village": "Madikeri"
            },
            "business_category": "Poultry",
            "margin_capital": 500000,
            "project_cost": 500000
        }

        with patch("app.services.business_analysis_service.get_recommendations", return_value=[]):
            response = self.client.post("/api/business/analyze", json=payload)
            self.assertEqual(response.status_code, 200)

            data = response.json()
            self.assertEqual(data["finance"]["loan_amount"], 0)
            self.assertEqual(data["finance"]["emi"], 0)
            self.assertEqual(data["finance"]["total_interest"], 0)

    def test_04_analyze_business_missing_field(self):
        """Test Pydantic validation for missing required fields."""
        payload = {
            "location": {
                "state": "Karnataka"
            },
            "margin_capital": 100000
            # Missing business_category and project_cost
        }

        response = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_05_analyze_business_negative_project_cost(self):
        """Test validation for negative project cost."""
        payload = {
            "location": {
                "state": "Karnataka",
                "district": "Kodagu",
                "village": "Madikeri"
            },
            "business_category": "Agriculture",
            "margin_capital": 100000,
            "project_cost": -50000
        }

        response = self.client.post("/api/business/analyze", json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
