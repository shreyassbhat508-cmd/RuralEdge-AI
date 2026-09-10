import unittest
from app.schemas.business import LocationInput, MarketInfo, SchemeInfo
from app.services.feasibility_scoring_service import calculate_feasibility_score


class TestFeasibilityScoringEngine(unittest.TestCase):

    def test_high_feasibility_scenario(self):
        """Test high feasibility case (30% equity, high-demand category, zero competitors, matched scheme)."""
        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        scheme_info = SchemeInfo(
            status="matched",
            recommended_scheme="Dairy Entrepreneurship Development Scheme",
            match_score=85,
            reasons=["State match", "Category match"],
        )
        market_info = MarketInfo(
            status="available",
            competitor_count=0,
            radius_km=10,
            market_reach_score=85,
            competition_score=95,
        )

        result = calculate_feasibility_score(
            project_cost=1_000_000,
            margin_capital=300_000,
            loan_amount=700_000,
            emi=13_860.57,
            business_category="Dairy",
            location=location,
            scheme_info=scheme_info,
            market_info=market_info,
        )

        self.assertEqual(result.level, "High")
        self.assertGreaterEqual(result.score, 75)

        # Component breakdown check
        comp = result.components
        self.assertGreaterEqual(comp.market, 80)
        self.assertEqual(comp.competition, 95)
        self.assertGreaterEqual(comp.financial, 85)
        self.assertEqual(comp.location, 85)
        self.assertGreaterEqual(comp.affordability, 70)

        # Reasons check
        self.assertTrue(any("High growth potential category" in r for r in result.reasons))
        self.assertTrue(any("Low competitor density" in r for r in result.reasons))

    def test_medium_feasibility_scenario(self):
        """Test medium feasibility case (10% equity, moderate category, fallback competition)."""
        location = LocationInput(state="Karnataka", district="Kodagu", village=None)
        scheme_info = SchemeInfo(
            status="no_match",
            recommended_scheme=None,
            match_score=0,
            reasons=[],
        )
        market_info = MarketInfo(
            status="pending",
            competitor_count=0,
            radius_km=10,
            market_reach_score=0,
        )

        result = calculate_feasibility_score(
            project_cost=1_000_000,
            margin_capital=100_000,
            loan_amount=900_000,
            emi=17_820.73,
            business_category="Retail Store",
            location=location,
            scheme_info=scheme_info,
            market_info=market_info,
        )

        self.assertEqual(result.level, "Medium")
        self.assertTrue(50 <= result.score < 75)

        # Verify fallback reason when competitor dataset is pending
        self.assertTrue(any("Competitor location dataset unavailable" in r for r in result.reasons))

    def test_low_feasibility_scenario(self):
        """Test low feasibility case (2% equity, high competition, unlisted generic category)."""
        location = LocationInput(state="Karnataka", district="Kodagu", village=None)
        scheme_info = SchemeInfo(
            status="no_match",
            recommended_scheme=None,
            match_score=0,
            reasons=[],
        )
        market_info = MarketInfo(
            status="available",
            competitor_count=8,
            radius_km=10,
            market_reach_score=20,
            competition_score=35,
        )

        result = calculate_feasibility_score(
            project_cost=10_000_000,
            margin_capital=200_000,
            loan_amount=9_800_000,
            emi=194_000.0,
            business_category="Custom Enterprise",
            location=location,
            scheme_info=scheme_info,
            market_info=market_info,
        )

        self.assertEqual(result.level, "Low")
        self.assertLess(result.score, 50)

        # Check low equity warning reason
        self.assertTrue(any("Very low equity contribution" in r for r in result.reasons))
        self.assertTrue(any("High competitor density" in r for r in result.reasons))

    def test_zero_loan_amount_100_percent_self_funded(self):
        """Test 100% self-funded project has maximum affordability score."""
        location = LocationInput(state="Karnataka", district="Kodagu", village="Madikeri")
        result = calculate_feasibility_score(
            project_cost=500_000,
            margin_capital=500_000,
            loan_amount=0,
            emi=0,
            business_category="Dairy",
            location=location,
        )

        self.assertEqual(result.components.affordability, 100)
        self.assertTrue(any("100% self-funded project" in r for r in result.reasons))


if __name__ == "__main__":
    unittest.main()
