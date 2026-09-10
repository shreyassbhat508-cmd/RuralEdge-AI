import os
import unittest
from unittest.mock import patch, MagicMock

# Set fallback dummy env vars for tests
if "SUPABASE_URL" not in os.environ:
    os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
if "SUPABASE_KEY" not in os.environ:
    os.environ["SUPABASE_KEY"] = "mock-key-12345"

from fastapi.testclient import TestClient
from app.main import app
from app.schemas.business import LocationInput
from app.services.google_places_service import (
    get_google_places_competitor_analysis,
    haversine_distance,
    _calculate_competition_score,
)


class TestGooglePlacesService(unittest.TestCase):

    def test_01_haversine_distance_calculation(self):
        """Test Haversine geodesic distance calculation (Requirement 7)."""
        # Distance between Bangalore and Mysore is ~125-135 km
        dist = haversine_distance(12.9716, 77.5946, 12.2958, 76.6394)
        self.assertTrue(120.0 <= dist <= 140.0)

    def test_02_missing_api_key_returns_unavailable(self):
        """Test behavior when API key is missing (Requirement 4)."""
        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")

        with patch.dict(os.environ, {}, clear=True):
            result = get_google_places_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.status, "unavailable")
            self.assertEqual(result.source, "google_places")
            self.assertIsNone(result.competitor_count)
            self.assertEqual(result.competitors, [])
            self.assertIsNone(result.competition_score)
            self.assertEqual(result.message, "Google Places data is currently unavailable.")

    @patch("httpx.Client.get")
    def test_03_google_api_failure_returns_unavailable(self, mock_get):
        """Test behavior when Google API returns HTTP error (Requirement 5)."""
        mock_get.side_effect = Exception("Google Places API Quota Exceeded")

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "mock-key-123"}, clear=True):
            result = get_google_places_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.status, "unavailable")
            self.assertEqual(result.source, "google_places")
            self.assertIsNone(result.competitor_count)
            self.assertEqual(result.competitors, [])
            self.assertIsNone(result.competition_score)
            self.assertEqual(result.message, "Google Places data is currently unavailable.")

    @patch("httpx.Client.get")
    def test_04_timeout_network_failure(self, mock_get):
        """Test behavior on network timeout (Requirement 6)."""
        mock_get.side_effect = Exception("ReadTimeoutError")

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "mock-key-123"}, clear=True):
            result = get_google_places_competitor_analysis(location, "Bakery", radius_km=10)

            self.assertEqual(result.status, "unavailable")
            self.assertIsNone(result.competitor_count)
            self.assertIsNone(result.competition_score)

    @patch("httpx.Client.get")
    def test_05_successful_google_places_response(self, mock_get):
        """Test successful response with multiple competitors (Requirements 1, 2, 8, 9)."""
        geocode_resp = MagicMock()
        geocode_resp.status_code = 200
        geocode_resp.json.return_value = {
            "status": "OK",
            "results": [{"geometry": {"location": {"lat": 12.4244, "lng": 75.7382}}}]
        }

        places_resp = MagicMock()
        places_resp.status_code = 200
        places_resp.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "place_id": "p2",
                    "name": "Coorg Dairy Chilling Plant",
                    "formatted_address": "Industrial Suburb, Madikeri",
                    "rating": 4.1,
                    "user_ratings_total": 18,
                    "types": ["food_processing"],
                    "geometry": {"location": {"lat": 12.4500, "lng": 75.7500}}
                },
                {
                    "place_id": "p1",
                    "name": "Madikeri Milk Union",
                    "formatted_address": "College Road, Madikeri",
                    "rating": 4.5,
                    "user_ratings_total": 42,
                    "types": ["dairy_store"],
                    "geometry": {"location": {"lat": 12.4300, "lng": 75.7400}}
                }
            ]
        }

        mock_get.side_effect = [geocode_resp, places_resp]

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "mock-key-123"}, clear=True):
            result = get_google_places_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.status, "success")
            self.assertEqual(result.source, "google_places")
            self.assertEqual(result.competitor_count, 2)
            self.assertEqual(len(result.competitors), 2)
            self.assertIsNotNone(result.competition_score)

            # Check sorting by distance
            self.assertEqual(result.competitors[0].name, "Madikeri Milk Union")
            self.assertEqual(result.competitors[1].name, "Coorg Dairy Chilling Plant")
            self.assertLessEqual(result.competitors[0].distance_km, result.competitors[1].distance_km)

            # Check normalized structure
            comp1 = result.competitors[0]
            self.assertEqual(comp1.category, "Dairy Store")
            self.assertEqual(comp1.source, "google_places")
            self.assertEqual(comp1.rating, 4.5)
            self.assertEqual(comp1.user_ratings_total, 42)

    @patch("httpx.Client.get")
    def test_06_zero_competitors_found(self, mock_get):
        """Test when Google Places successfully searches and returns 0 competitors (Requirement 3)."""
        geocode_resp = MagicMock()
        geocode_resp.status_code = 200
        geocode_resp.json.return_value = {
            "status": "OK",
            "results": [{"geometry": {"location": {"lat": 12.4244, "lng": 75.7382}}}]
        }

        places_resp = MagicMock()
        places_resp.status_code = 200
        places_resp.json.return_value = {"status": "ZERO_RESULTS", "results": []}

        mock_get.side_effect = [geocode_resp, places_resp]

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "mock-key-123"}, clear=True):
            result = get_google_places_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.status, "success")
            self.assertEqual(result.competitor_count, 0)
            self.assertEqual(result.competitors, [])
            self.assertEqual(result.competition_score, 95)  # 0 competitors -> 95 score

    def test_07_competition_score_calculation(self):
        """Test competition density score formula (Requirement 9)."""
        # 0 competitors -> 95
        self.assertEqual(_calculate_competition_score([], 0), 95)

    @patch("app.services.business_analysis_service.get_google_places_competitor_analysis")
    @patch("app.services.business_analysis_service.get_recommendations")
    def test_08_api_business_analyze_success(self, mock_rec, mock_places):
        """Test POST /api/business/analyze when Google Places succeeds (Requirement 10)."""
        mock_rec.return_value = []
        mock_places.return_value = get_google_places_competitor_analysis(
            LocationInput(state="Karnataka", district="Kodagu", village="Madikeri"),
            "Dairy",
            10,
        )

        client = TestClient(app)
        payload = {
            "location": {"state": "Karnataka", "district": "Kodagu", "village": "Madikeri"},
            "business_category": "Dairy",
            "margin_capital": 100000,
            "project_cost": 1000000,
        }

        response = client.post("/api/business/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("market", data)
        self.assertEqual(data["market"]["source"], "google_places")

    @patch("app.services.business_analysis_service.get_recommendations")
    def test_09_api_business_analyze_unavailable(self, mock_rec):
        """Test POST /api/business/analyze when Google Places is unavailable (Requirement 11)."""
        mock_rec.return_value = []

        client = TestClient(app)
        payload = {
            "location": {"state": "Karnataka", "district": "Kodagu", "village": "Madikeri"},
            "business_category": "Dairy",
            "margin_capital": 100000,
            "project_cost": 1000000,
        }

        with patch.dict(os.environ, {}, clear=True):
            response = client.post("/api/business/analyze", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("market", data)
            self.assertEqual(data["market"]["status"], "unavailable")
            self.assertIsNone(data["market"]["competitor_count"])
            self.assertIsNone(data["market"]["competition_score"])
            self.assertEqual(data["market"]["message"], "Google Places data is currently unavailable.")


if __name__ == "__main__":
    unittest.main()
