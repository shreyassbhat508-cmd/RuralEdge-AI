"""Unit tests for the RuralEdge Finance Engine.

Executes comprehensive tests across normal loans, zero-interest loans, zero-loan projects,
zero-revenue projects, loss-making businesses, boundary conditions, input validation errors,
and the 'Small Dairy Farm' benchmark example.
"""

import unittest
from finance import (
    FinanceInput,
    FinanceResult,
    FinanceValidationError,
    calculate_financials,
)


class TestFinanceEngine(unittest.TestCase):
    """Test suite covering financial metric calculations and validation rules."""

    def test_01_normal_loan_with_interest(self) -> None:
        """TEST 1: Normal loan with standard reducing balance interest calculation."""
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
        self.assertEqual(res.business_name, "Poultry Farm")
        self.assertEqual(res.loan_required, 150000.0)
        self.assertEqual(res.capital_gap, 0.0)
        self.assertEqual(res.own_contribution_percentage, 25.0)
        self.assertEqual(res.financing_percentage, 75.0)

        # Expected EMI formula check
        # r = 0.12/12 = 0.01, n = 36. EMI = 150000 * 0.01 * (1.01^36) / (1.01^36 - 1) = 4982.17
        self.assertAlmostEqual(res.monthly_emi, 4982.17, delta=0.5)
        self.assertGreater(res.total_interest, 0.0)
        self.assertGreater(res.monthly_profit, 0.0)

    def test_02_zero_interest_loan(self) -> None:
        """TEST 2: Zero-interest loan calculation."""
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

    def test_03_no_loan(self) -> None:
        """TEST 3: Fully self-funded project with zero loan."""
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

    def test_04_zero_revenue(self) -> None:
        """TEST 4: Pre-operational or zero revenue scenario."""
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

    def test_05_operating_costs_greater_than_revenue(self) -> None:
        """TEST 5: Operating costs exceeding revenue (negative contribution margin)."""
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

    def test_06_zero_project_cost(self) -> None:
        """TEST 6: Zero project cost boundary case."""
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

    def test_07_invalid_negative_input(self) -> None:
        """TEST 7: Negative monetary values raise validation error."""
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
        self.assertTrue(any("total_project_cost cannot be negative" in err for err in ctx.exception.errors))

    def test_08_loan_amount_greater_than_funding_requirement(self) -> None:
        """TEST 8: Surplus capital funding (own + loan > total_project_cost) raises validation error."""
        inp = FinanceInput(
            business_name="Over-Funded Enterprise",
            total_project_cost=100000.0,
            own_contribution=60000.0,
            loan_amount=50000.0,  # 60k + 50k = 110k > 100k
            annual_interest_rate=10.0,
            loan_tenure_months=24,
            monthly_revenue=20000.0,
            monthly_operating_cost=10000.0,
            monthly_fixed_cost=3000.0,
        )
        with self.assertRaises(FinanceValidationError) as ctx:
            calculate_financials(inp)
        self.assertTrue(any("exceeds total_project_cost" in err for err in ctx.exception.errors))

    def test_09_positive_profitable_business_small_dairy_farm(self) -> None:
        """TEST 9: Benchmark 'Small Dairy Farm' example from Phase F1 specification."""
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

        self.assertEqual(res.business_name, "Small Dairy Farm")
        self.assertEqual(res.total_project_cost, 500000.0)
        self.assertEqual(res.own_contribution, 100000.0)
        self.assertEqual(res.loan_amount, 400000.0)
        self.assertEqual(res.loan_required, 400000.0)
        self.assertEqual(res.capital_gap, 0.0)

        # Percentages
        self.assertEqual(res.own_contribution_percentage, 20.0)
        self.assertEqual(res.financing_percentage, 80.0)

        # Loan EMI checks
        # raw_emi = P*r*(1+r)^n / ((1+r)^n - 1) = 8498.8178... -> rounds to 8498.82
        self.assertEqual(res.monthly_emi, 8498.82)
        # total_repayment = round(8498.82 * 60, 2) = 509929.20
        self.assertAlmostEqual(res.total_repayment, 509929.20, delta=0.01)
        # total_interest = round(509929.20 - 400000.0, 2) = 109929.20
        self.assertAlmostEqual(res.total_interest, 109929.20, delta=0.01)

        # Monthly & Annual Profit
        # monthly_total_cost = round(35000 + 10000 + 8498.82, 2) = 53498.82
        self.assertEqual(res.monthly_total_cost, 53498.82)
        # monthly_profit = round(80000 - 53498.82, 2) = 26501.18
        self.assertEqual(res.monthly_profit, 26501.18)
        self.assertEqual(res.annual_revenue, 960000.0)
        # annual_profit = round(26501.18 * 12, 2) = 318014.16
        self.assertEqual(res.annual_profit, 318014.16)
        self.assertEqual(res.profit_margin_percentage, 33.13)

        # Operating Break-Even (Contribution margin = 80k - 35k = 45k, CM Ratio = 45k/80k = 0.5625. BE Rev = 10k / 0.5625 = 17777.78)
        self.assertIsNotNone(res.break_even_revenue)
        self.assertEqual(res.break_even_revenue, 17777.78)

        # Payback period (500,000 / 26,501.18 = 18.87 months)
        self.assertIsNotNone(res.estimated_payback_months)
        self.assertEqual(res.estimated_payback_months, 18.87)

    def test_10_loss_making_business(self) -> None:
        """TEST 10: Loss-making enterprise scenario."""
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
