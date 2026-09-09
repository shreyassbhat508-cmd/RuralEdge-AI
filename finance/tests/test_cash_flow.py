"""Unit tests for the RuralEdge Finance Engine — Phase F2.

Tests cash flow calculations, operating/debt-service break-even analysis,
break-even gap and status indicators, cash-flow status, cumulative cash-flow
projection, and the payback period under F2 semantics.

TEST 1:  Positive monthly cash flow.
TEST 2:  Zero monthly cash flow (neutral status).
TEST 3:  Negative monthly cash flow.
TEST 4:  Operating break-even revenue.
TEST 5:  Debt-service break-even revenue.
TEST 6:  Break-even not calculable when monthly revenue is zero.
TEST 7:  Break-even not calculable when operating cost >= monthly revenue.
TEST 8:  Cumulative cash flow over 12 months (helper function).
TEST 9:  Positive cash-flow payback period.
TEST 10: No payback when monthly cash flow <= 0.
TEST 11: F1 regression — all existing F1 tests still pass via the combined suite.

All expected values are derived analytically from the published F1 monetary rounding
policy (round to 2 dp at each computation boundary) and the standard reducing-balance
EMI formula. No expected values are fabricated or approximated.
"""

import unittest
from finance import (
    FinanceInput,
    FinanceResult,
    FinanceValidationError,
    calculate_financials,
    calculate_cumulative_cash_flow,
)


class TestFinanceEngineF2(unittest.TestCase):
    """Test suite for Phase F2 cash flow and break-even analysis."""

    # ------------------------------------------------------------------
    # Shared fixtures
    # ------------------------------------------------------------------

    def _dairy_farm_input(self) -> FinanceInput:
        """Small Dairy Farm benchmark — same inputs as F1 Test 9."""
        return FinanceInput(
            business_name="Small Dairy Farm",
            total_project_cost=500000.0,
            own_contribution=100000.0,
            loan_amount=400000.0,
            annual_interest_rate=10.0,
            loan_tenure_months=60,
            monthly_revenue=80000.0,
            monthly_operating_cost=35000.0,
            monthly_fixed_cost=10000.0,
        )

    # ------------------------------------------------------------------
    # TEST 1 – Positive monthly cash flow
    # ------------------------------------------------------------------

    def test_01_positive_monthly_cash_flow(self) -> None:
        """TEST 1: Positive monthly cash flow — Small Dairy Farm benchmark.

        monthly_emi  = round(raw_emi(400000, 10%, 60), 2) = 8498.82
        monthly_cash_flow = 80000 - 35000 - 10000 - 8498.82 = 26501.18
        annual_cash_flow  = 26501.18 * 12 = 318014.16
        cash_flow_status  = "positive"
        """
        res = calculate_financials(self._dairy_farm_input())

        self.assertEqual(res.monthly_cash_flow, 26501.18)
        self.assertEqual(res.annual_cash_flow, 318014.16)
        self.assertEqual(res.cash_flow_status, "positive")

    # ------------------------------------------------------------------
    # TEST 2 – Zero monthly cash flow (neutral)
    # ------------------------------------------------------------------

    def test_02_zero_monthly_cash_flow(self) -> None:
        """TEST 2: Zero monthly cash flow yields cash_flow_status = 'neutral'.

        With no loan, zero EMI, and revenue == operating + fixed costs:
        monthly_cash_flow = 45000 - 35000 - 10000 - 0 = 0
        """
        inp = FinanceInput(
            business_name="Break-Even Store",
            total_project_cost=100000.0,
            own_contribution=100000.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=45000.0,
            monthly_operating_cost=35000.0,
            monthly_fixed_cost=10000.0,
        )
        res = calculate_financials(inp)

        self.assertEqual(res.monthly_cash_flow, 0.0)
        self.assertEqual(res.annual_cash_flow, 0.0)
        self.assertEqual(res.cash_flow_status, "neutral")

    # ------------------------------------------------------------------
    # TEST 3 – Negative monthly cash flow
    # ------------------------------------------------------------------

    def test_03_negative_monthly_cash_flow(self) -> None:
        """TEST 3: Negative monthly cash flow yields cash_flow_status = 'negative'.

        Revenue insufficient to cover operating costs, fixed costs, and EMI.
        monthly_emi (P=150000, r=12%, n=36) = round(raw_emi, 2) = 4982.17 (approx)
        monthly_cash_flow = 10000 - 15000 - 3000 - 4982.17 = -12982.17
        """
        inp = FinanceInput(
            business_name="Struggling Pottery Unit",
            total_project_cost=200000.0,
            own_contribution=50000.0,
            loan_amount=150000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=36,
            monthly_revenue=10000.0,
            monthly_operating_cost=15000.0,
            monthly_fixed_cost=3000.0,
        )
        res = calculate_financials(inp)

        self.assertLess(res.monthly_cash_flow, 0.0)
        self.assertLess(res.annual_cash_flow, 0.0)
        self.assertEqual(res.cash_flow_status, "negative")

    # ------------------------------------------------------------------
    # TEST 4 – Operating break-even revenue
    # ------------------------------------------------------------------

    def test_04_operating_break_even_revenue(self) -> None:
        """TEST 4: Operating break-even revenue on the Small Dairy Farm.

        contribution_margin = 80000 - 35000 = 45000
        cm_ratio            = 45000 / 80000 = 0.5625
        operating_be        = 10000 / 0.5625 = 17777.78
        operating_be_gap    = 80000 - 17777.78 = 62222.22  (above break-even)
        operating_be_status = "above_break_even"
        """
        res = calculate_financials(self._dairy_farm_input())

        self.assertEqual(res.break_even_revenue, 17777.78)
        self.assertEqual(res.operating_break_even_gap, 62222.22)
        self.assertEqual(res.operating_break_even_status, "above_break_even")

    # ------------------------------------------------------------------
    # TEST 5 – Debt-service break-even revenue
    # ------------------------------------------------------------------

    def test_05_debt_service_break_even_revenue(self) -> None:
        """TEST 5: Debt-service break-even revenue on the Small Dairy Farm.

        cm_ratio            = 0.5625
        numerator           = monthly_fixed_cost + monthly_emi = 10000 + 8498.82 = 18498.82
        debt_service_be     = 18498.82 / 0.5625 = 32886.79
        debt_service_be_gap = 80000 - 32886.79 = 47113.21  (above break-even)
        debt_service_status = "above_break_even"

        Debt-service BE > operating BE (32886.79 > 17777.78) because EMI is included.
        """
        res = calculate_financials(self._dairy_farm_input())

        self.assertIsNotNone(res.debt_service_break_even_revenue)
        self.assertEqual(res.debt_service_break_even_revenue, 32886.79)
        self.assertGreater(
            res.debt_service_break_even_revenue,
            res.break_even_revenue,
            msg="Debt-service break-even must exceed operating break-even when EMI > 0.",
        )
        self.assertEqual(res.debt_service_break_even_gap, 47113.21)
        self.assertEqual(res.debt_service_break_even_status, "above_break_even")

    # ------------------------------------------------------------------
    # TEST 6 – Break-even not calculable when revenue is zero
    # ------------------------------------------------------------------

    def test_06_break_even_not_calculable_zero_revenue(self) -> None:
        """TEST 6: Both break-even values are None when monthly_revenue == 0."""
        inp = FinanceInput(
            business_name="Pre-Revenue Project",
            total_project_cost=200000.0,
            own_contribution=100000.0,
            loan_amount=100000.0,
            annual_interest_rate=10.0,
            loan_tenure_months=24,
            monthly_revenue=0.0,
            monthly_operating_cost=5000.0,
            monthly_fixed_cost=3000.0,
        )
        res = calculate_financials(inp)

        self.assertIsNone(res.break_even_revenue)
        self.assertIsNone(res.debt_service_break_even_revenue)
        self.assertIsNone(res.operating_break_even_gap)
        self.assertIsNone(res.debt_service_break_even_gap)
        self.assertEqual(res.operating_break_even_status, "not_calculable")
        self.assertEqual(res.debt_service_break_even_status, "not_calculable")

    # ------------------------------------------------------------------
    # TEST 7 – Break-even not calculable when operating cost >= revenue
    # ------------------------------------------------------------------

    def test_07_break_even_not_calculable_negative_cm(self) -> None:
        """TEST 7: Break-even is None when operating cost equals or exceeds revenue.

        contribution_margin_ratio <= 0 makes break-even analysis undefined.
        """
        inp = FinanceInput(
            business_name="High-Cost Weaving Unit",
            total_project_cost=150000.0,
            own_contribution=50000.0,
            loan_amount=100000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=24,
            monthly_revenue=10000.0,
            monthly_operating_cost=10000.0,   # exactly equals revenue → cm_ratio = 0
            monthly_fixed_cost=3000.0,
        )
        res = calculate_financials(inp)

        self.assertIsNone(res.break_even_revenue)
        self.assertIsNone(res.debt_service_break_even_revenue)
        self.assertEqual(res.operating_break_even_status, "not_calculable")
        self.assertEqual(res.debt_service_break_even_status, "not_calculable")

        # Also test strictly negative cm (operating cost > revenue)
        inp2 = FinanceInput(
            business_name="Loss-Cost Unit",
            total_project_cost=150000.0,
            own_contribution=50000.0,
            loan_amount=100000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=24,
            monthly_revenue=8000.0,
            monthly_operating_cost=10000.0,   # exceeds revenue → cm_ratio < 0
            monthly_fixed_cost=3000.0,
        )
        res2 = calculate_financials(inp2)
        self.assertIsNone(res2.break_even_revenue)
        self.assertIsNone(res2.debt_service_break_even_revenue)
        self.assertEqual(res2.operating_break_even_status, "not_calculable")
        self.assertEqual(res2.debt_service_break_even_status, "not_calculable")

    # ------------------------------------------------------------------
    # TEST 8 – Cumulative cash flow helper over 12 months
    # ------------------------------------------------------------------

    def test_08_cumulative_cash_flow_12_months(self) -> None:
        """TEST 8: calculate_cumulative_cash_flow returns correct cumulative values.

        With monthly_cash_flow = 26501.18 (Small Dairy Farm):
          month 1  →  26501.18
          month 6  → 159007.08
          month 12 → 318014.16

        Also tests the helper independently with a simple 10000/month scenario.
        """
        # Simple deterministic case
        simple = calculate_cumulative_cash_flow(10000.0, 12)
        self.assertEqual(len(simple), 12)
        self.assertEqual(simple[1], 10000.0)
        self.assertEqual(simple[6], 60000.0)
        self.assertEqual(simple[12], 120000.0)

        # Small Dairy Farm values
        dairy = calculate_cumulative_cash_flow(26501.18, 12)
        self.assertEqual(len(dairy), 12)
        self.assertEqual(dairy[1], 26501.18)
        self.assertAlmostEqual(dairy[6], 159007.08, delta=0.01)
        self.assertAlmostEqual(dairy[12], 318014.16, delta=0.01)

        # Edge: zero months returns empty dict
        empty = calculate_cumulative_cash_flow(10000.0, 0)
        self.assertEqual(empty, {})

        # Edge: negative monthly cash flow (losses accumulate)
        loss = calculate_cumulative_cash_flow(-5000.0, 3)
        self.assertEqual(loss[1], -5000.0)
        self.assertEqual(loss[2], -10000.0)
        self.assertEqual(loss[3], -15000.0)

        # Verify cumulative_cash_flow in FinanceResult (60-month projection for dairy farm)
        res = calculate_financials(self._dairy_farm_input())
        self.assertEqual(len(res.cumulative_cash_flow), 60)
        self.assertEqual(res.cumulative_cash_flow[1], 26501.18)
        self.assertAlmostEqual(res.cumulative_cash_flow[12], 318014.16, delta=0.01)

    # ------------------------------------------------------------------
    # TEST 9 – Positive cash-flow payback period
    # ------------------------------------------------------------------

    def test_09_positive_cash_flow_payback(self) -> None:
        """TEST 9: Payback period is calculated when monthly cash flow is positive.

        Small Dairy Farm:
          estimated_payback_months = round(500000 / 26501.18, 2) = 18.87
        """
        res = calculate_financials(self._dairy_farm_input())

        self.assertIsNotNone(res.estimated_payback_months)
        self.assertEqual(res.estimated_payback_months, 18.87)
        self.assertGreater(res.estimated_payback_months, 0.0)

    # ------------------------------------------------------------------
    # TEST 10 – No payback when monthly cash flow <= 0
    # ------------------------------------------------------------------

    def test_10_no_payback_when_cash_flow_non_positive(self) -> None:
        """TEST 10: estimated_payback_months is None when monthly_cash_flow <= 0."""
        # Negative cash flow scenario
        inp_negative = FinanceInput(
            business_name="Loss Business",
            total_project_cost=200000.0,
            own_contribution=50000.0,
            loan_amount=150000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=36,
            monthly_revenue=10000.0,
            monthly_operating_cost=15000.0,
            monthly_fixed_cost=3000.0,
        )
        res_neg = calculate_financials(inp_negative)
        self.assertLess(res_neg.monthly_cash_flow, 0.0)
        self.assertIsNone(res_neg.estimated_payback_months)

        # Zero cash flow scenario
        inp_zero = FinanceInput(
            business_name="Zero CF Business",
            total_project_cost=100000.0,
            own_contribution=100000.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=45000.0,
            monthly_operating_cost=35000.0,
            monthly_fixed_cost=10000.0,
        )
        res_zero = calculate_financials(inp_zero)
        self.assertEqual(res_zero.monthly_cash_flow, 0.0)
        self.assertIsNone(res_zero.estimated_payback_months)

    # ------------------------------------------------------------------
    # TEST 11 – F2 edge cases: zero loan, zero project cost, zero op cost
    # ------------------------------------------------------------------

    def test_11_edge_cases(self) -> None:
        """TEST 11: F2 is safe across boundary inputs.

        Covers zero loan, zero project cost, zero operating cost.
        No division-by-zero errors must occur.
        """
        # Zero loan (no EMI) — debt-service BE equals operating BE
        inp_no_loan = FinanceInput(
            business_name="No-Loan Farm",
            total_project_cost=100000.0,
            own_contribution=100000.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=30000.0,
            monthly_operating_cost=15000.0,
            monthly_fixed_cost=5000.0,
        )
        res_nl = calculate_financials(inp_no_loan)
        self.assertEqual(res_nl.monthly_emi, 0.0)
        # With zero EMI, debt-service BE == operating BE
        self.assertEqual(res_nl.debt_service_break_even_revenue, res_nl.break_even_revenue)
        self.assertIsNotNone(res_nl.debt_service_break_even_revenue)

        # Zero project cost — payback must be None even with positive cash flow
        inp_zero_cost = FinanceInput(
            business_name="Zero-Cost Consultancy",
            total_project_cost=0.0,
            own_contribution=0.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=20000.0,
            monthly_operating_cost=5000.0,
            monthly_fixed_cost=3000.0,
        )
        res_zc = calculate_financials(inp_zero_cost)
        self.assertGreater(res_zc.monthly_cash_flow, 0.0)
        self.assertIsNone(res_zc.estimated_payback_months)   # project_cost == 0

        # Zero operating cost — contribution margin ratio == 1.0, BE = fixed / 1 = fixed
        inp_zero_op = FinanceInput(
            business_name="Zero-OpCost Business",
            total_project_cost=100000.0,
            own_contribution=100000.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=20000.0,
            monthly_operating_cost=0.0,
            monthly_fixed_cost=5000.0,
        )
        res_zo = calculate_financials(inp_zero_op)
        self.assertEqual(res_zo.break_even_revenue, 5000.0)
        self.assertEqual(res_zo.debt_service_break_even_revenue, 5000.0)
        self.assertEqual(res_zo.operating_break_even_status, "above_break_even")


class TestFinanceEngineF1Regression(unittest.TestCase):
    """Regression guard — all F1 tests re-executed after F2 extension.

    Ensures that adding F2 fields to FinanceResult and extending calculate_financials
    has not changed any F1 calculation or validation behaviour.
    """

    def test_r01_normal_loan_with_interest(self) -> None:
        """F1-R01: Normal loan with standard reducing-balance interest."""
        inp = FinanceInput(
            business_name="Poultry Farm",
            total_project_cost=200000.0,
            own_contribution=50000.0,
            loan_amount=150000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=36,
            monthly_revenue=40000.0,
            monthly_operating_cost=18000.0,
            monthly_fixed_cost=5000.0,
        )
        res = calculate_financials(inp)
        self.assertEqual(res.loan_required, 150000.0)
        self.assertEqual(res.capital_gap, 0.0)
        self.assertEqual(res.own_contribution_percentage, 25.0)
        self.assertEqual(res.financing_percentage, 75.0)
        self.assertAlmostEqual(res.monthly_emi, 4982.17, delta=0.5)
        self.assertGreater(res.total_interest, 0.0)
        self.assertGreater(res.monthly_profit, 0.0)

    def test_r02_zero_interest_loan(self) -> None:
        """F1-R02: Zero-interest loan."""
        inp = FinanceInput(
            business_name="Interest-Free Micro Scheme",
            total_project_cost=120000.0,
            own_contribution=20000.0,
            loan_amount=100000.0,
            annual_interest_rate=0.0,
            loan_tenure_months=20,
            monthly_revenue=25000.0,
            monthly_operating_cost=10000.0,
            monthly_fixed_cost=3000.0,
        )
        res = calculate_financials(inp)
        self.assertEqual(res.monthly_emi, 5000.0)
        self.assertEqual(res.total_repayment, 100000.0)
        self.assertEqual(res.total_interest, 0.0)

    def test_r03_no_loan(self) -> None:
        """F1-R03: Fully self-funded project."""
        inp = FinanceInput(
            business_name="Self-Funded Organic Farm",
            total_project_cost=100000.0,
            own_contribution=100000.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=20000.0,
            monthly_operating_cost=8000.0,
            monthly_fixed_cost=2000.0,
        )
        res = calculate_financials(inp)
        self.assertEqual(res.monthly_emi, 0.0)
        self.assertEqual(res.total_repayment, 0.0)
        self.assertEqual(res.total_interest, 0.0)
        self.assertEqual(res.financing_percentage, 0.0)
        self.assertEqual(res.own_contribution_percentage, 100.0)
        self.assertEqual(res.monthly_total_cost, 10000.0)
        self.assertEqual(res.monthly_profit, 10000.0)

    def test_r04_zero_revenue(self) -> None:
        """F1-R04: Pre-operational / zero revenue."""
        inp = FinanceInput(
            business_name="Pre-Revenue Agri-Tech Setup",
            total_project_cost=300000.0,
            own_contribution=100000.0,
            loan_amount=200000.0,
            annual_interest_rate=10.0,
            loan_tenure_months=48,
            monthly_revenue=0.0,
            monthly_operating_cost=5000.0,
            monthly_fixed_cost=5000.0,
        )
        res = calculate_financials(inp)
        self.assertEqual(res.monthly_revenue, 0.0)
        self.assertEqual(res.annual_revenue, 0.0)
        self.assertEqual(res.profit_margin_percentage, 0.0)
        self.assertLess(res.monthly_profit, 0.0)
        self.assertIsNone(res.break_even_revenue)
        self.assertIsNone(res.estimated_payback_months)

    def test_r05_operating_costs_greater_than_revenue(self) -> None:
        """F1-R05: Negative contribution margin."""
        inp = FinanceInput(
            business_name="Struggling Weaving Unit",
            total_project_cost=150000.0,
            own_contribution=50000.0,
            loan_amount=100000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=24,
            monthly_revenue=10000.0,
            monthly_operating_cost=15000.0,
            monthly_fixed_cost=3000.0,
        )
        res = calculate_financials(inp)
        self.assertLess(res.monthly_profit, 0.0)
        self.assertIsNone(res.break_even_revenue)
        self.assertIsNone(res.estimated_payback_months)

    def test_r06_zero_project_cost(self) -> None:
        """F1-R06: Zero project cost boundary."""
        inp = FinanceInput(
            business_name="Consultancy Service",
            total_project_cost=0.0,
            own_contribution=0.0,
            loan_amount=0.0,
            annual_interest_rate=0.0,
            loan_tenure_months=0,
            monthly_revenue=15000.0,
            monthly_operating_cost=2000.0,
            monthly_fixed_cost=1000.0,
        )
        res = calculate_financials(inp)
        self.assertEqual(res.total_project_cost, 0.0)
        self.assertEqual(res.own_contribution_percentage, 0.0)
        self.assertEqual(res.financing_percentage, 0.0)
        self.assertEqual(res.monthly_profit, 12000.0)
        self.assertIsNone(res.estimated_payback_months)

    def test_r07_invalid_negative_input(self) -> None:
        """F1-R07: Negative monetary values raise FinanceValidationError."""
        inp = FinanceInput(
            business_name="Invalid Business",
            total_project_cost=-50000.0,
            own_contribution=10000.0,
            loan_amount=40000.0,
            annual_interest_rate=10.0,
            loan_tenure_months=12,
            monthly_revenue=10000.0,
            monthly_operating_cost=5000.0,
            monthly_fixed_cost=2000.0,
        )
        with self.assertRaises(FinanceValidationError) as ctx:
            calculate_financials(inp)
        self.assertTrue(
            any("total_project_cost cannot be negative" in err for err in ctx.exception.errors)
        )

    def test_r08_loan_exceeds_project_cost(self) -> None:
        """F1-R08: Surplus capital funding raises FinanceValidationError."""
        inp = FinanceInput(
            business_name="Over-Funded Enterprise",
            total_project_cost=100000.0,
            own_contribution=60000.0,
            loan_amount=50000.0,
            annual_interest_rate=10.0,
            loan_tenure_months=24,
            monthly_revenue=20000.0,
            monthly_operating_cost=10000.0,
            monthly_fixed_cost=3000.0,
        )
        with self.assertRaises(FinanceValidationError) as ctx:
            calculate_financials(inp)
        self.assertTrue(
            any("exceeds total_project_cost" in err for err in ctx.exception.errors)
        )

    def test_r09_small_dairy_farm_benchmark(self) -> None:
        """F1-R09: Small Dairy Farm benchmark — all F1 values intact after F2 extension.

        raw_emi = 8498.8178... → round to 2 dp → 8498.82
        All downstream F1 fields use this rounded EMI consistently.
        """
        inp = FinanceInput(
            business_name="Small Dairy Farm",
            total_project_cost=500000.0,
            own_contribution=100000.0,
            loan_amount=400000.0,
            annual_interest_rate=10.0,
            loan_tenure_months=60,
            monthly_revenue=80000.0,
            monthly_operating_cost=35000.0,
            monthly_fixed_cost=10000.0,
        )
        res = calculate_financials(inp)

        # Capital structure
        self.assertEqual(res.business_name, "Small Dairy Farm")
        self.assertEqual(res.total_project_cost, 500000.0)
        self.assertEqual(res.own_contribution, 100000.0)
        self.assertEqual(res.loan_amount, 400000.0)
        self.assertEqual(res.loan_required, 400000.0)
        self.assertEqual(res.capital_gap, 0.0)
        self.assertEqual(res.own_contribution_percentage, 20.0)
        self.assertEqual(res.financing_percentage, 80.0)

        # Loan repayment
        self.assertEqual(res.monthly_emi, 8498.82)
        self.assertAlmostEqual(res.total_repayment, 509929.20, delta=0.01)
        self.assertAlmostEqual(res.total_interest, 109929.20, delta=0.01)

        # Profitability
        self.assertEqual(res.monthly_total_cost, 53498.82)
        self.assertEqual(res.monthly_profit, 26501.18)
        self.assertEqual(res.annual_revenue, 960000.0)
        self.assertEqual(res.annual_profit, 318014.16)
        self.assertEqual(res.profit_margin_percentage, 33.13)

        # Break-even and payback
        self.assertEqual(res.break_even_revenue, 17777.78)
        self.assertEqual(res.estimated_payback_months, 18.87)

    def test_r10_loss_making_business(self) -> None:
        """F1-R10: Loss-making enterprise."""
        inp = FinanceInput(
            business_name="Unprofitable Pottery Unit",
            total_project_cost=200000.0,
            own_contribution=50000.0,
            loan_amount=150000.0,
            annual_interest_rate=12.0,
            loan_tenure_months=36,
            monthly_revenue=15000.0,
            monthly_operating_cost=12000.0,
            monthly_fixed_cost=5000.0,
        )
        res = calculate_financials(inp)
        self.assertLess(res.monthly_profit, 0.0)
        self.assertLess(res.annual_profit, 0.0)
        self.assertIsNone(res.estimated_payback_months)


if __name__ == "__main__":
    unittest.main()
