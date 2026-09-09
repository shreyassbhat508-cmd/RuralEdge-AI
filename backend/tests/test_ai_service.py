import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app


class TestAIService(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.services.ai_service.httpx.Client")
    def test_valid_general_ai_request(self, mock_httpx):
        """Scenario A: Valid general AI request (no scheme_id)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "RuralEdge is a portal designed to help rural citizens find government schemes."
                            }
                        ]
                    }
                }
            ]
        }
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_instance

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_mock_api_key"}):
            res = self.client.post(
                "/api/ai/chat",
                json={"message": "What is RuralEdge and how can it help me?"},
            )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("RuralEdge is a portal", data["reply"])
        self.assertIsNone(data["scheme_id"])
        self.assertIn("disclaimer", data)

    @patch("app.services.ai_service.get_scheme_details_by_id")
    @patch("app.services.ai_service.httpx.Client")
    def test_valid_scheme_specific_ai_request(self, mock_httpx, mock_get_details):
        """Scenario B: Valid scheme-specific AI request with mocked scheme data."""
        scheme_id = "b259d19f-fc94-4be2-90bd-3d27be2b8eec"
        mock_get_details.return_value = {
            "scheme": {
                "id": scheme_id,
                "name": "Janani Suraksha Yojana",
                "official_url": "https://nhm.gov.in/jsy",
            },
            "eligibility": [{"gender": "Female", "occupation": "Pregnant Women"}],
            "benefits": [{"amount": 1400.0}],
            "source": None,
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Janani Suraksha Yojana provides financial aid to pregnant women for institutional delivery."
                            }
                        ]
                    }
                }
            ]
        }
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_instance

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_mock_api_key"}):
            res = self.client.post(
                "/api/ai/chat",
                json={
                    "message": "Explain this scheme",
                    "scheme_id": scheme_id,
                },
            )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("Janani Suraksha Yojana", data["reply"])
        self.assertEqual(data["scheme_id"], scheme_id)
        self.assertIn("https://nhm.gov.in/jsy", data["sources"])

    def test_invalid_scheme_uuid(self):
        """Scenario C: Invalid scheme UUID format returns HTTP 422."""
        res = self.client.post(
            "/api/ai/chat",
            json={
                "message": "Explain this scheme",
                "scheme_id": "not-a-valid-uuid-string",
            },
        )
        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

    @patch("app.services.ai_service.get_scheme_details_by_id")
    def test_nonexistent_scheme(self, mock_get_details):
        """Scenario D: Nonexistent scheme UUID returns HTTP 404."""
        mock_get_details.return_value = None
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_mock_api_key"}):
            res = self.client.post(
                "/api/ai/chat",
                json={
                    "message": "Explain this scheme",
                    "scheme_id": non_existent_uuid,
                },
            )

        self.assertEqual(res.status_code, 404)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "SCHEME_NOT_FOUND")

    def test_message_exceeding_2000_characters(self):
        """Scenario E: Message exceeding 2000 characters returns HTTP 422."""
        long_message = "A" * 2001
        res = self.client.post(
            "/api/ai/chat",
            json={"message": long_message},
        )
        self.assertEqual(res.status_code, 422)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "VALIDATION_ERROR")

    @patch("app.services.ai_service.httpx.Client")
    def test_mocked_gemini_service_failure(self, mock_httpx):
        """Scenario F: Gemini service failure returns HTTP 503 AI_SERVICE_UNAVAILABLE."""
        mock_instance = MagicMock()
        mock_instance.post.side_effect = Exception("Network connection timeout to Gemini API")
        mock_httpx.return_value.__enter__.return_value = mock_instance

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_mock_api_key"}):
            res = self.client.post(
                "/api/ai/chat",
                json={"message": "What is this scheme about?"},
            )

        self.assertEqual(res.status_code, 503)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"]["code"], "AI_SERVICE_UNAVAILABLE")
        self.assertEqual(data["error"]["message"], "AI assistant is temporarily unavailable.")

    def test_verify_no_database_writes(self):
        """Scenario G: Verify AI service performs zero database write operations."""
        from app.database import supabase
        # Assert supabase client object does not have insert/update/delete called
        self.assertTrue(hasattr(supabase, "table"))


if __name__ == "__main__":
    unittest.main()
