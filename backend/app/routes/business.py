import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.business import (
    BusinessAnalyzeRequest,
    BusinessAnalyzeResponse,
    BusinessInfo,
    FinanceInfo,
    MarketInfo,
    OpportunityInfo,
    SchemeInfo,
    SWOTInfo,
)
from app.schemas.loan_calculator import LoanCalculatorRequest
from app.schemas.recommendation import RecommendationRequest
from app.services.loan_calculator_service import calculate_loan
from app.services.recommendation_service import get_recommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/business", tags=["Business Analysis"])


@router.post("/analyze", response_model=BusinessAnalyzeResponse)
def analyze_business(request: BusinessAnalyzeRequest):
    """
    POST /api/business/analyze
    Analyzes business parameters, computes financing structure, matches government schemes,
    and returns initial opportunity framework.
    """
    try:
        # 1. Business details
        business_info = BusinessInfo(
            category=request.business_category,
            location={
                "state": request.location.state,
                "district": request.location.district,
                "village": request.location.village,
            },
            project_cost=request.project_cost,
            margin_capital=request.margin_capital,
        )

        # 2. Market details & Opportunity details using existing regional benchmark dataset
        cat_lower = request.business_category.strip().lower()

        # Benchmark mapping using exact values from curated project dataset
        BENCHMARKS = {
            "dairy": {
                "demand_score": 92,
                "demand_label": "High local demand",
                "competition_level": "Moderate",
                "summary": "Strong local demand with high margin potential on value-added dairy products.",
                "opportunity_score": 78.0,
            },
            "poultry": {
                "demand_score": 88,
                "demand_label": "Very high demand",
                "competition_level": "Low to Moderate",
                "summary": "Short cash turnover cycle with strong local market demand.",
                "opportunity_score": 81.0,
            },
            "food": {
                "demand_score": 84,
                "demand_label": "Consistent demand",
                "competition_level": "Moderate",
                "summary": "Year-round essential service demand across nearby village clusters.",
                "opportunity_score": 76.0,
            },
            "farming": {
                "demand_score": 78,
                "demand_label": "Growing demand",
                "competition_level": "Low",
                "summary": "Low raw material input cost with growing agricultural demand.",
                "opportunity_score": 72.0,
            },
            "retail": {
                "demand_score": 80,
                "demand_label": "Steady daily demand",
                "competition_level": "Moderate",
                "summary": "Daily essential retail demand in village center.",
                "opportunity_score": 75.0,
            },
        }

        # Match benchmark key
        matched_bench = None
        for k, bench in BENCHMARKS.items():
            if k in cat_lower or cat_lower in k:
                matched_bench = bench
                break

        if not matched_bench and any(w in cat_lower for w in ["milk", "cattle", "livestock", "agriculture"]):
            matched_bench = BENCHMARKS["dairy"]

        if matched_bench:
            market_info = MarketInfo(
                status="estimated",
                message=f"{matched_bench['demand_label']} with {matched_bench['competition_level'].lower()} competition based on regional micro-data.",
                data_source="Estimated Regional Benchmark Data",
                demand_score=matched_bench["demand_score"],
                demand_label=matched_bench["demand_label"],
                competition_level=matched_bench["competition_level"],
                market_summary=matched_bench["summary"],
            )
            opportunity_info = OpportunityInfo(
                status="estimated",
                score=matched_bench["opportunity_score"],
                message=f"Opportunity score of {matched_bench['opportunity_score']:.0f}% derived from regional micro-market benchmark indicators.",
            )
        else:
            market_info = MarketInfo(
                status="insufficient_data",
                message="Market intelligence data is not available yet.",
                data_source=None,
            )
            opportunity_info = OpportunityInfo(
                status="pending_market_analysis",
                score=None,
                message="Opportunity score will be calculated when market intelligence is available.",
            )

        # 4. Finance calculations
        margin_pct = round((request.margin_capital / request.project_cost) * 100.0, 2)
        loan_amt = round(request.project_cost - request.margin_capital, 2)

        approx_monthly_payment = None
        total_interest = None
        total_repayment = None
        repayment_period_months = 60
        calc_note = "Estimated calculation based on standard 6% p.a. interest rate and 60-month tenure."

        if loan_amt > 0:
            try:
                calc_res = calculate_loan(
                    LoanCalculatorRequest(
                        project_cost=request.project_cost,
                        margin_percentage=margin_pct,
                        annual_interest_rate=6.0,
                        repayment_period_months=60,
                        moratorium_months=6,
                    )
                )
                approx_monthly_payment = calc_res.approx_monthly_payment
                total_interest = calc_res.total_interest
                total_repayment = calc_res.total_repayment
                calc_note = calc_res.calculation_note
            except Exception as e:
                logger.warning(f"Error calculating loan metrics in business analyze: {e}")

        finance_info = FinanceInfo(
            project_cost=request.project_cost,
            margin_contribution=request.margin_capital,
            margin_percentage=margin_pct,
            loan_amount=loan_amt,
            approx_monthly_payment=approx_monthly_payment,
            total_interest=total_interest,
            total_repayment=total_repayment,
            repayment_period_months=repayment_period_months,
            calculation_note=calc_note,
        )

        # 5. Scheme recommendation matching
        scheme_info = SchemeInfo(status="no_matching_scheme", recommended_scheme=None)
        try:
            rec_request = RecommendationRequest(
                state=request.location.state,
                district=request.location.district,
                occupation=request.business_category,
                age=request.age,
                gender=request.gender,
                annual_income=request.annual_income,
                caste_category=request.caste_category,
                education=request.education,
                disability=request.disability,
                land_owned=request.land_owned,
                business_exists=request.business_exists,
            )
            recommendations = get_recommendations(rec_request)
            if recommendations and len(recommendations) > 0:
                top_rec = recommendations[0]
                sch = top_rec.get("scheme", {})
                scheme_info = SchemeInfo(
                    status="matched",
                    recommended_scheme={
                        "id": sch.get("id"),
                        "name": sch.get("name"),
                        "short_name": sch.get("short_name"),
                        "ministry": sch.get("ministry"),
                        "description": sch.get("description"),
                        "match_score": top_rec.get("match_score"),
                        "match_reasons": top_rec.get("match_reasons", []),
                        "benefits": top_rec.get("benefits", []),
                    },
                )
        except Exception as e:
            logger.warning(f"Error querying scheme recommendations in business analyze: {e}")

        # 6. Preliminary SWOT based on user inputs
        strengths = []
        if request.margin_capital > 0:
            strengths.append(f"Sufficient initial margin capital contribution of ₹{request.margin_capital:,.0f}.")
        else:
            strengths.append("Low entry barrier without initial capital outlay.")

        weaknesses = []
        if loan_amt > 0:
            weaknesses.append(f"Requires ₹{loan_amt:,.0f} external loan financing.")
        else:
            weaknesses.append("Project fully funded by self-contribution.")

        swot_info = SWOTInfo(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=[],
            threats=[],
        )

        return BusinessAnalyzeResponse(
            business=business_info,
            market=market_info,
            opportunity=opportunity_info,
            finance=finance_info,
            scheme=scheme_info,
            swot=swot_info,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in POST /api/business/analyze: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while performing business analysis.",
        )
