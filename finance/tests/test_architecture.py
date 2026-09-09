"""Unit tests for the RuralEdge Finance Engine — 4-Step Architecture.

Tests the new 4-step financial assessment pipeline:
    Step 1 — Project Requirement (project cost, loan required)
    Step 2 — Scheme Financing (loan cap, funding gap)
    Step 3 — Repayment and Profitability (EMI, cash flow, break-even)
    Step 4 — Financial Feasibility (status classification)

TEST 01: Project cost calculation from components.
TEST 02: Loan requirement from project cost and own contribution.
TEST 03: Scheme loan cap partially covers the requirement (funding gap).
TEST 04: Scheme loan cap fully covers the requirement (no gap).
TEST 05: No scheme supplied — engine does not invent terms.
TEST 06: Zero loan required — EMI equals zero.
TEST 07: EMI calculation reusing verified F1 formula (P=400k, 10%, 60m).
TEST 08: Positive monthly cash flow scenario.
TEST 09: Negative monthly cash flow → financial_status = "not_feasible".
TEST 10: Positive business but funding gap → financial_status = "modify".
TEST 11: Fully funded and profitable business → financial_status = "feasible".
TEST 12: Zero revenue — no division-by-zero errors.

All expected values are derived analytically.
No values are fabricated or approximated.
"""

import unittest
from finance import (
    FinanceValidationError,
    ProjectInput,
    SchemeFinance,
    calculate_project_requirement,
    apply_scheme_financing,
    calculate_financial_assessment,
)


class TestFourStepArchitecture(unittest.TestCase):
    """Test suite for the 4-step financial assessment pipeline."""

    # ------------------------------------------------------------------
    # Shared fixtures
    # ------------------------------------------------------------------

    def _make_project_input(
        self,
        *,
        business_name: str = "Test Business",
        fixed_asset_cost: float = 0.0,
        setup_cost: float = 0.0,
        initial_inventory_cost: float = 0.0,
        initial_working_capital: float = 0.0,
        own_contribution: float = 0.0,
        expected_monthly_revenue: float = 0.0,
        expected_monthly_operating_cost: float = 0.0,
        expected_monthly_fixed_cost: float = 0.0,
    ) -> ProjectInput:
        return ProjectInput(
            business_name=business_name,
            business_category="Agriculture",
            location="Rural Karnataka",
            fixed_asset_cost=fixed_asset_cost,
            setup_cost=setup_cost,
            initial_inventory_cost=initial_inventory_cost,
            initial_working_capital=initial_working_capital,
            own_contribution=own_contribution,
            expected_monthly_revenue=expected_monthly_revenue,
            expected_monthly_operating_cost=expected_monthly_operating_cost,
            expected_monthly_fixed_cost=expected_monthly_fixed_cost,
        )

    def _make_scheme(
        self,
        *,
        scheme_name: str = "PM-MUDRA Kishore",
        maximum_loan_amount: float = 500000.0,
        interest_rate: float = 7.0,
        tenure_months: int = 36,
        moratorium_months: int = 0,
    ) -> SchemeFinance:
        return SchemeFinance(
            scheme_name=scheme_name,
            maximum_loan_amount=maximum_loan_amount,
            interest_rate=interest_rate,
            tenure_months=tenure_months,
            moratorium_months=moratorium_months,
        )

    # ------------------------------------------------------------------
    # TEST 01 — Project cost calculation
    # ------------------------------------------------------------------

    def test_01_project_cost_calculation(self) -> None:
        """TEST 01: project_cost = fixed_assets + setup + inventory + working_capital.

        fixed_asset_cost       = 200,000
        setup_cost             =  50,000
        initial_inventory_cost =  50,000
        initial_working_capital = 100,000
        ─────────────────────────────────
        project_cost           = 400,000
        """
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            setup_cost=50000.0,
            initial_inventory_cost=50000.0,
            initial_working_capital=100000.0,
            own_contribution=0.0,
        )
        req = calculate_project_requirement(inp)

        self.assertEqual(req.project_cost, 400000.0)
        self.assertEqual(req.fixed_asset_cost, 200000.0)
        self.assertEqual(req.setup_cost, 50000.0)
        self.assertEqual(req.initial_inventory_cost, 50000.0)
        self.assertEqual(req.initial_working_capital, 100000.0)

    # ------------------------------------------------------------------
    # TEST 02 — Loan requirement
    # ------------------------------------------------------------------

    def test_02_loan_requirement(self) -> None:
        """TEST 02: loan_required = project_cost − own_contribution.

        project_cost     = 400,000
        own_contribution = 100,000
        ─────────────────────────────────
        loan_required    = 300,000
        """
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            setup_cost=50000.0,
            initial_inventory_cost=50000.0,
            initial_working_capital=100000.0,
            own_contribution=100000.0,
        )
        req = calculate_project_requirement(inp)

        self.assertEqual(req.project_cost, 400000.0)
        self.assertEqual(req.own_contribution, 100000.0)
        self.assertEqual(req.loan_required, 300000.0)
        self.assertEqual(req.own_contribution_surplus, 0.0)

    # ------------------------------------------------------------------
    # TEST 03 — Scheme loan cap partially covers requirement
    # ------------------------------------------------------------------

    def test_03_scheme_loan_cap_partial(self) -> None:
        """TEST 03: applicable_loan = min(300000, 250000) = 250000; funding_gap = 50000."""
        financing = apply_scheme_financing(
            loan_required=300000.0,
            scheme_finance=self._make_scheme(maximum_loan_amount=250000.0),
        )

        self.assertEqual(financing.requested_loan, 300000.0)
        self.assertEqual(financing.scheme_loan_cap, 250000.0)
        self.assertEqual(financing.applicable_loan, 250000.0)
        self.assertEqual(financing.funding_gap, 50000.0)
        self.assertTrue(financing.has_confirmed_financing)

    # ------------------------------------------------------------------
    # TEST 04 — Scheme loan cap fully covers requirement
    # ------------------------------------------------------------------

    def test_04_scheme_loan_cap_full(self) -> None:
        """TEST 04: applicable_loan = min(300000, 400000) = 300000; funding_gap = 0."""
        financing = apply_scheme_financing(
            loan_required=300000.0,
            scheme_finance=self._make_scheme(maximum_loan_amount=400000.0),
        )

        self.assertEqual(financing.applicable_loan, 300000.0)
        self.assertEqual(financing.funding_gap, 0.0)
        self.assertTrue(financing.has_confirmed_financing)

    # ------------------------------------------------------------------
    # TEST 05 — No scheme supplied
    # ------------------------------------------------------------------

    def test_05_no_scheme_supplied(self) -> None:
        """TEST 05: When no scheme is supplied, the engine does not invent any terms.

        scheme_name, scheme_loan_cap, interest_rate, tenure_months must all be None.
        has_confirmed_financing must be False.
        """
        financing = apply_scheme_financing(loan_required=200000.0, scheme_finance=None)

        self.assertIsNone(financing.scheme_name)
        self.assertIsNone(financing.scheme_loan_cap)
        self.assertIsNone(financing.interest_rate)
        self.assertIsNone(financing.tenure_months)
        self.assertFalse(financing.has_confirmed_financing)
        # Full requirement is noted, no cap applied
        self.assertEqual(financing.applicable_loan, 200000.0)
        self.assertEqual(financing.funding_gap, 0.0)

        # In FinancialAssessment: no scheme terms should appear as None
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            own_contribution=0.0,
            expected_monthly_revenue=30000.0,
            expected_monthly_operating_cost=10000.0,
            expected_monthly_fixed_cost=5000.0,
        )
        assessment = calculate_financial_assessment(inp, scheme_finance=None)

        self.assertIsNone(assessment.scheme_name)
        self.assertIsNone(assessment.scheme_loan_cap)
        self.assertIsNone(assessment.interest_rate)
        self.assertIsNone(assessment.tenure_months)
        # loan_required > 0 and no confirmed financing → status must be "modify"
        self.assertGreater(assessment.loan_required, 0)
        self.assertEqual(assessment.financial_status, "modify")

    # ------------------------------------------------------------------
    # TEST 06 — Zero loan (own contribution covers full project cost)
    # ------------------------------------------------------------------

    def test_06_zero_loan(self) -> None:
        """TEST 06: When own_contribution >= project_cost, loan_required = 0 and EMI = 0."""
        inp = self._make_project_input(
            fixed_asset_cost=100000.0,
            setup_cost=50000.0,
            own_contribution=200000.0,      # surplus — covers entire project
            expected_monthly_revenue=30000.0,
            expected_monthly_operating_cost=12000.0,
            expected_monthly_fixed_cost=5000.0,
        )
        req = calculate_project_requirement(inp)

        self.assertEqual(req.loan_required, 0.0)
        self.assertEqual(req.own_contribution_surplus, 50000.0)  # 200k - 150k

        assessment = calculate_financial_assessment(inp, scheme_finance=None)

        self.assertEqual(assessment.monthly_emi, 0.0)
        self.assertEqual(assessment.total_repayment, 0.0)
        self.assertEqual(assessment.total_interest, 0.0)
        # Fully self-funded and profitable → "feasible"
        self.assertGreater(assessment.monthly_cash_flow, 0.0)
        self.assertEqual(assessment.financial_status, "feasible")

    # ------------------------------------------------------------------
    # TEST 07 — EMI reuse (verified F1 formula)
    # ------------------------------------------------------------------

    def test_07_emi_reuses_f1_formula(self) -> None:
        """TEST 07: P=400,000 @ 10% annual for 60 months → EMI = 8498.82 (F1 verified).

        raw_emi = 400000 * (0.10/12) * (1 + 0.10/12)^60
                  / ((1 + 0.10/12)^60 - 1)
                = 8498.8178...
                → round to 2 dp = 8498.82
        """
        inp = self._make_project_input(
            fixed_asset_cost=400000.0,
            own_contribution=0.0,
            expected_monthly_revenue=80000.0,
            expected_monthly_operating_cost=35000.0,
            expected_monthly_fixed_cost=10000.0,
        )
        scheme = self._make_scheme(
            maximum_loan_amount=500000.0,
            interest_rate=10.0,
            tenure_months=60,
        )
        assessment = calculate_financial_assessment(inp, scheme)

        # Loan is fully covered (applicable_loan = 400000)
        self.assertEqual(assessment.applicable_loan, 400000.0)
        # EMI must match the F1-verified value exactly
        self.assertEqual(assessment.monthly_emi, 8498.82)

    # ------------------------------------------------------------------
    # TEST 08 — Positive monthly cash flow
    # ------------------------------------------------------------------

    def test_08_positive_monthly_cash_flow(self) -> None:
        """TEST 08: Profitable business with positive monthly cash flow.

        Project:   fixed=200k + setup=50k + inventory=50k + wc=100k = 400k
        Own:       100k  →  loan_required = 300k
        Scheme:    cap=400k, rate=7%, tenure=36m → EMI = 9263.13
        Revenue:   60,000  Op: 25,000  Fixed: 8,000
        monthly_cash_flow = 60000 - 25000 - 8000 - 9263.13 = 17736.87
        """
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            setup_cost=50000.0,
            initial_inventory_cost=50000.0,
            initial_working_capital=100000.0,
            own_contribution=100000.0,
            expected_monthly_revenue=60000.0,
            expected_monthly_operating_cost=25000.0,
            expected_monthly_fixed_cost=8000.0,
        )
        scheme = self._make_scheme(maximum_loan_amount=400000.0, interest_rate=7.0, tenure_months=36)
        assessment = calculate_financial_assessment(inp, scheme)

        self.assertEqual(assessment.loan_required, 300000.0)
        self.assertEqual(assessment.applicable_loan, 300000.0)
        self.assertEqual(assessment.funding_gap, 0.0)
        self.assertEqual(assessment.monthly_emi, 9263.13)
        self.assertEqual(assessment.monthly_cash_flow, 17736.87)
        self.assertGreater(assessment.monthly_cash_flow, 0.0)

    # ------------------------------------------------------------------
    # TEST 09 — Negative monthly cash flow → not_feasible
    # ------------------------------------------------------------------

    def test_09_negative_cash_flow_not_feasible(self) -> None:
        """TEST 09: Costs exceed revenue → financial_status = 'not_feasible'.

        monthly_revenue = 15,000
        op_cost         = 20,000
        fixed_cost      =  5,000
        EMI             =     0  (own-funded)
        monthly_cash_flow = 15000 - 20000 - 5000 - 0 = -10000
        """
        inp = self._make_project_input(
            fixed_asset_cost=100000.0,
            own_contribution=100000.0,    # fully self-funded
            expected_monthly_revenue=15000.0,
            expected_monthly_operating_cost=20000.0,
            expected_monthly_fixed_cost=5000.0,
        )
        assessment = calculate_financial_assessment(inp, scheme_finance=None)

        self.assertEqual(assessment.monthly_cash_flow, -10000.0)
        self.assertLess(assessment.monthly_cash_flow, 0.0)
        self.assertEqual(assessment.financial_status, "not_feasible")

    # ------------------------------------------------------------------
    # TEST 10 — Positive business but funding gap → modify
    # ------------------------------------------------------------------

    def test_10_positive_business_with_funding_gap_modify(self) -> None:
        """TEST 10: Cash flow > 0 but scheme cap creates a funding gap → 'modify'.

        Project: 400k  Own: 100k  loan_required = 300k
        Scheme cap: 250k  → applicable_loan = 250k, funding_gap = 50k
        EMI (P=250k, 7%, 36m) = 7719.27
        monthly_cash_flow = 60000 - 25000 - 8000 - 7719.27 = 19280.73 (> 0)
        financial_status = "modify"  (positive CF but funding gap > 0)
        """
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            setup_cost=50000.0,
            initial_inventory_cost=50000.0,
            initial_working_capital=100000.0,
            own_contribution=100000.0,
            expected_monthly_revenue=60000.0,
            expected_monthly_operating_cost=25000.0,
            expected_monthly_fixed_cost=8000.0,
        )
        scheme = self._make_scheme(maximum_loan_amount=250000.0, interest_rate=7.0, tenure_months=36)
        assessment = calculate_financial_assessment(inp, scheme)

        self.assertEqual(assessment.loan_required, 300000.0)
        self.assertEqual(assessment.applicable_loan, 250000.0)
        self.assertEqual(assessment.funding_gap, 50000.0)
        self.assertEqual(assessment.monthly_emi, 7719.27)
        self.assertEqual(assessment.monthly_cash_flow, 19280.73)
        self.assertGreater(assessment.monthly_cash_flow, 0.0)
        self.assertEqual(assessment.financial_status, "modify")

    # ------------------------------------------------------------------
    # TEST 11 — Fully funded and profitable → feasible
    # ------------------------------------------------------------------

    def test_11_fully_funded_profitable_feasible(self) -> None:
        """TEST 11: Loan fully covered, cash flow positive → financial_status = 'feasible'.

        Project: 400k  Own: 100k  loan_required = 300k
        Scheme cap: 400k → applicable_loan = 300k, funding_gap = 0
        EMI (P=300k, 7%, 36m) = 9263.13
        monthly_cash_flow = 60000 - 25000 - 8000 - 9263.13 = 17736.87
        financial_status = "feasible"
        """
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            setup_cost=50000.0,
            initial_inventory_cost=50000.0,
            initial_working_capital=100000.0,
            own_contribution=100000.0,
            expected_monthly_revenue=60000.0,
            expected_monthly_operating_cost=25000.0,
            expected_monthly_fixed_cost=8000.0,
        )
        scheme = self._make_scheme(maximum_loan_amount=400000.0, interest_rate=7.0, tenure_months=36)
        assessment = calculate_financial_assessment(inp, scheme)

        self.assertEqual(assessment.loan_required, 300000.0)
        self.assertEqual(assessment.applicable_loan, 300000.0)
        self.assertEqual(assessment.funding_gap, 0.0)
        self.assertEqual(assessment.monthly_emi, 9263.13)
        self.assertEqual(assessment.monthly_cash_flow, 17736.87)
        self.assertGreater(assessment.monthly_cash_flow, 0.0)
        self.assertEqual(assessment.financial_status, "feasible")

        # Verify moratorium is stored (even with 0 months) and note is present
        self.assertEqual(assessment.moratorium_months, 0)
        self.assertIn("moratorium", assessment.moratorium_repayment_note.lower())

    # ------------------------------------------------------------------
    # TEST 12 — Zero revenue (no division-by-zero)
    # ------------------------------------------------------------------

    def test_12_zero_revenue_no_division_errors(self) -> None:
        """TEST 12: Zero revenue must not cause any division-by-zero errors.

        - break_even and debt-service break-even must be None.
        - profit_margin_percentage must be 0.0 (not an error).
        - financial_status must be 'not_feasible' (monthly_cash_flow < 0).
        """
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            own_contribution=50000.0,
            expected_monthly_revenue=0.0,
            expected_monthly_operating_cost=10000.0,
            expected_monthly_fixed_cost=5000.0,
        )
        scheme = self._make_scheme(maximum_loan_amount=200000.0, interest_rate=10.0, tenure_months=48)

        # Must not raise any exception
        assessment = calculate_financial_assessment(inp, scheme)

        self.assertEqual(assessment.monthly_revenue, 0.0)
        self.assertEqual(assessment.profit_margin_percentage, 0.0)
        self.assertIsNone(assessment.operating_break_even_revenue)
        self.assertIsNone(assessment.debt_service_break_even_revenue)
        self.assertLess(assessment.monthly_cash_flow, 0.0)
        self.assertEqual(assessment.financial_status, "not_feasible")
        self.assertIsNone(assessment.estimated_payback_months)

    # ------------------------------------------------------------------
    # Additional edge cases
    # ------------------------------------------------------------------

    def test_edge_surplus_own_contribution(self) -> None:
        """Edge: own_contribution > project_cost → surplus captured, loan_required = 0."""
        inp = self._make_project_input(
            fixed_asset_cost=100000.0,
            own_contribution=150000.0,
        )
        req = calculate_project_requirement(inp)
        self.assertEqual(req.loan_required, 0.0)
        self.assertEqual(req.own_contribution_surplus, 50000.0)

    def test_edge_moratorium_stored(self) -> None:
        """Edge: moratorium_months is stored and surfaced in the result without calculation."""
        scheme = self._make_scheme(moratorium_months=6)
        inp = self._make_project_input(
            fixed_asset_cost=200000.0,
            own_contribution=50000.0,
            expected_monthly_revenue=40000.0,
            expected_monthly_operating_cost=15000.0,
            expected_monthly_fixed_cost=5000.0,
        )
        assessment = calculate_financial_assessment(inp, scheme)

        self.assertEqual(assessment.moratorium_months, 6)
        # Note must explicitly mention moratorium is future work
        self.assertIn("not yet implemented", assessment.moratorium_repayment_note)

    def test_edge_scheme_validation_negative_rate(self) -> None:
        """Edge: negative interest rate in SchemeFinance raises FinanceValidationError."""
        from finance import validate_scheme_finance
        scheme = SchemeFinance(
            scheme_name="Invalid Scheme",
            maximum_loan_amount=100000.0,
            interest_rate=-5.0,
            tenure_months=24,
        )
        with self.assertRaises(FinanceValidationError) as ctx:
            validate_scheme_finance(scheme)
        self.assertTrue(any("interest_rate" in e for e in ctx.exception.errors))

    def test_edge_project_input_negative_cost(self) -> None:
        """Edge: negative cost component raises FinanceValidationError."""
        inp = self._make_project_input(fixed_asset_cost=-50000.0)
        with self.assertRaises(FinanceValidationError) as ctx:
            calculate_project_requirement(inp)
        self.assertTrue(any("fixed_asset_cost" in e for e in ctx.exception.errors))


if __name__ == "__main__":
    unittest.main()
