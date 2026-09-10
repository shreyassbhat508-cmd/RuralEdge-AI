import os
import unittest
from unittest.mock import patch, MagicMock
from app.schemas.business import CompetitorDetail, LocationInput
from app.services.competitor_service import (
    get_competitor_analysis,
    _haversine_distance,
    _CACHE,
)


class TestCompetitorServiceOSMFallback(unittest.TestCase):

    def setUp(self):
        _CACHE.clear()

    def test_01_haversine_distance_calculation(self):
        """Test Haversine geodesic distance calculation."""
        dist = _haversine_distance(12.9716, 77.5946, 12.2958, 76.6394)
        self.assertTrue(120.0 <= dist <= 140.0)

    @patch("app.services.competitor_service._geocode_nominatim")
    @patch("app.services.competitor_service._fetch_overpass_places")
    def test_02_osm_fallback_when_google_key_missing(self, mock_overpass, mock_geocode):
        """Test OSM fallback when Google API key is missing."""
        mock_geocode.return_value = (12.4244, 75.7382)
        mock_overpass.return_value = [
            CompetitorDetail(
                name="Madikeri Milk Center",
                address="Madikeri Main Road",
                category="Dairy",
                distance_km=1.2,
                rating=None,
                user_ratings_total=None,
            ),
            CompetitorDetail(
                name="Coorg Farmers Dairy",
                address="Near Bus Stand",
                category="Dairy",
                distance_km=3.4,
                rating=None,
                user_ratings_total=None,
            ),
        ]

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {}, clear=True):
            result = get_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.source, "osm")
            self.assertEqual(result.status, "success")
            self.assertEqual(result.competitor_count, 2)
            self.assertEqual(len(result.competitors), 2)
            self.assertEqual(result.competitors[0].name, "Madikeri Milk Center")
            self.assertGreater(result.competition_score, 50)

    @patch("app.services.competitor_service._fetch_google_places")
    @patch("app.services.competitor_service._geocode_google")
    @patch("app.services.competitor_service._geocode_nominatim")
    @patch("app.services.competitor_service._fetch_overpass_places")
    def test_03_osm_fallback_when_google_api_fails(
        self, mock_overpass, mock_nominatim, mock_geocode_google, mock_google_places
    ):
        """Test OSM fallback when Google Places API throws an error."""
        mock_geocode_google.return_value = (12.4244, 75.7382)
        mock_google_places.side_effect = Exception("Google API Quota Exceeded")

        mock_nominatim.return_value = (12.4244, 75.7382)
        mock_overpass.return_value = [
            CompetitorDetail(
                name="OSM Dairy Cooperative",
                address="Madikeri",
                category="Dairy",
                distance_km=2.1,
                rating=None,
                user_ratings_total=None,
            )
        ]

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {"GOOGLE_PLACES_API_KEY": "mock-key"}, clear=True):
            result = get_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.source, "osm")
            self.assertEqual(result.status, "success")
            self.assertEqual(result.competitor_count, 1)
            self.assertEqual(result.competitors[0].name, "OSM Dairy Cooperative")

    @patch("app.services.competitor_service._geocode_google")
    @patch("app.services.competitor_service._fetch_google_places")
    def test_04_google_places_preferred_when_available(self, mock_google_places, mock_geocode):
        """Test Google Places is preferred when API key is present and call succeeds."""
        mock_geocode.return_value = (12.4244, 75.7382)
        mock_google_places.return_value = [
            CompetitorDetail(
                name="Google Places Dairy",
                address="Madikeri",
                category="Dairy",
                distance_km=0.8,
                rating=4.6,
                user_ratings_total=30,
            )
        ]

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {"GOOGLE_PLACES_API_KEY": "mock-key"}, clear=True):
            result = get_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.source, "google_places")
            self.assertEqual(result.status, "success")
            self.assertEqual(result.competitor_count, 1)
            self.assertEqual(result.competitors[0].name, "Google Places Dairy")
            self.assertEqual(result.competitors[0].rating, 4.6)

    @patch("app.services.competitor_service._geocode_nominatim")
    def test_05_fallback_unavailable_when_both_fail(self, mock_nominatim):
        """Test fallback unavailable status when both Google Places and OSM fail."""
        mock_nominatim.side_effect = Exception("Network offline")

        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        with patch.dict(os.environ, {}, clear=True):
            result = get_competitor_analysis(location, "Dairy", radius_km=10)

            self.assertEqual(result.source, "fallback_unavailable")
            self.assertEqual(result.status, "unavailable")
            self.assertEqual(result.competitor_count, 0)
            self.assertEqual(result.competition_score, 70)


if __name__ == "__main__":
    unittest.main()
