import unittest
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import _evaluate_scheme_recommendation, _is_eligibility_compatible, _is_state_match


class TestRecommendationEngine(unittest.TestCase):

    def test_strong_match(self):
        """Scenario A: Strong match - User satisfies all criteria yielding high score (> 80)."""
        scheme = {
            "id": "scheme-001",
            "name": "Kisan Credit Scheme",
            "states": ["Karnataka", "Tamil Nadu"],
        }
        eligibility = [
            {
                "id": "elig-001",
                "scheme_id": "scheme-001",
                "min_age": 18,
                "max_age": 60,
                "gender": "all",
                "occupation": "farmer",
                "income_max": 300000,
                "caste_category": "all",
                "land_required": True,
            }
        ]
        request = RecommendationRequest.model_validate({
            "state": "Karnataka",
            "age": 30,
            "gender": "female",
            "occupation": "farmer",
            "annual_income": 150000.0,
            "land_owned": True,
        })

        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertGreaterEqual(res["match_score"], 80)
        self.assertIn("User state is supported by the scheme.", res["match_reasons"])
        self.assertIn("User age is within the eligible age range.", res["match_reasons"])
        self.assertIn("Occupation matches the eligibility requirement.", res["match_reasons"])

    def test_clear_eligibility_conflict(self):
        """Scenario B: Clear eligibility conflict - User fails mandatory criteria (age out of range)."""
        scheme = {
            "id": "scheme-002",
            "name": "Youth Skill Scheme",
            "states": ["Karnataka"],
        }
        eligibility = [
            {
                "id": "elig-002",
                "scheme_id": "scheme-002",
                "min_age": 18,
                "max_age": 25,
            }
        ]
        request = RecommendationRequest.model_validate({
            "state": "Karnataka",
            "age": 45,  # Exceeds max_age 25
        })

        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNone(res)  # Excluded due to clear conflict

    def test_missing_user_information(self):
        """Scenario C: Missing user information - Unprovided user fields yield partial score & warnings."""
        scheme = {
            "id": "scheme-003",
            "name": "Women Self-Help Scheme",
            "states": ["Karnataka"],
        }
        eligibility = [
            {
                "id": "elig-003",
                "scheme_id": "scheme-003",
                "gender": "female",
                "income_max": 200000,
            }
        ]
        request = RecommendationRequest.model_validate({
            "state": "Karnataka",
            "gender": "female",
            # annual_income is missing (None)
        })

        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertIn("Annual income was not provided; income criteria could not be fully verified.", res["warnings"])

    def test_scheme_with_unknown_eligibility(self):
        """Scenario D: Scheme with unknown eligibility information (0 eligibility records)."""
        scheme = {
            "id": "scheme-004",
            "name": "General Welfare Scheme",
            "states": ["Karnataka"],
        }
        eligibility = []  # No eligibility records in database

        request = RecommendationRequest.model_validate({
            "state": "Karnataka",
            "age": 30,
        })

        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertIn("Eligibility information is not available for this scheme.", res["warnings"])

    def test_location_match(self):
        """Scenario E: Location match - User state matches scheme states list."""
        scheme = {
            "id": "scheme-005",
            "name": "State Specific Support",
            "states": ["Karnataka", "Kerala"],
        }
        eligibility = [
            {
                "id": "elig-005",
                "scheme_id": "scheme-005",
            }
        ]
        request = RecommendationRequest.model_validate({"state": "Karnataka"})

        self.assertTrue(_is_state_match(scheme["states"], request.state))
        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertIn("User state is supported by the scheme.", res["match_reasons"])

    def test_location_information_unavailable(self):
        """Scenario F: Location information unavailable - Scheme states is NULL/empty."""
        scheme = {
            "id": "scheme-006",
            "name": "National General Scheme",
            "states": None,  # State info unavailable
        }
        eligibility = [
            {
                "id": "elig-006",
                "scheme_id": "scheme-006",
            }
        ]
        request = RecommendationRequest.model_validate({"state": "Karnataka"})

        self.assertTrue(_is_state_match(scheme["states"], request.state))
        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertIn("State-specific eligibility information is not available.", res["warnings"])

    def test_multiple_eligibility_records(self):
        """Scenario G: Multiple eligibility records - User matches one of alternative eligibility sets (OR logic)."""
        scheme = {
            "id": "scheme-007",
            "name": "Multi-Category Artisan Support",
            "states": ["Karnataka"],
        }
        eligibility = [
            {
                "id": "elig-007-a",
                "scheme_id": "scheme-007",
                "occupation": "weaver",
                "caste_category": "SC",
            },
            {
                "id": "elig-007-b",
                "scheme_id": "scheme-007",
                "occupation": "potter",
                "caste_category": "OBC",
            },
        ]
        # User is a potter (conflicts with Record A occupation, matches Record B)
        request = RecommendationRequest.model_validate({
            "state": "Karnataka",
            "occupation": "potter",
            "caste_category": "OBC",
        })

        res = _evaluate_scheme_recommendation(scheme, eligibility, request)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertIn("Occupation matches the eligibility requirement.", res["match_reasons"])
        self.assertIn("Caste category matches the eligibility requirement.", res["match_reasons"])



if __name__ == "__main__":
    unittest.main()
