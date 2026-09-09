import logging
from typing import Any, Dict, List, cast
from app.schemas.eligibility_check import EligibilityCheckResponse
from app.schemas.recommendation import RecommendationRequest
from app.schemas.scheme import SchemeResponse
from app.services.eligibility_service import get_eligibility_by_scheme_id
from app.services.recommendation_service import _is_eligibility_compatible, _is_state_match
from app.services.scheme_service import get_scheme_by_id

logger = logging.getLogger(__name__)


def check_scheme_eligibility(scheme_id: str, request: RecommendationRequest) -> EligibilityCheckResponse:
    """
    Checks user eligibility against a single specific government scheme using stored eligibility records in Supabase.
    """
    # 1. Fetch scheme from Supabase
    scheme_data = get_scheme_by_id(scheme_id)
    if not scheme_data:
        raise KeyError("Scheme not found")

    scheme = SchemeResponse.model_validate(scheme_data)

    # 2. Fetch eligibility records for this scheme
    elig_records = get_eligibility_by_scheme_id(scheme_id)

    warnings: List[str] = []

    # Check location eligibility
    state_match = _is_state_match(scheme_data.get("states"), request.state)

    if request.state and request.state.strip():
        states = scheme_data.get("states")
        has_states = False
        if isinstance(states, list):
            has_states = any(bool(st and str(st).strip()) for st in states)
        elif isinstance(states, str):
            has_states = bool(states.strip())

        if not has_states:
            warnings.append("State-specific eligibility information is not available.")

    if request.district and request.district.strip():
        warnings.append("District-specific eligibility information is not available.")

    # 3. Handle zero eligibility records case
    if not elig_records or len(elig_records) == 0:
        return EligibilityCheckResponse(
            scheme=scheme,
            eligible=False,
            reasons=[],
            warnings=["Eligibility information is not available for this scheme."],
        )

    # If state explicitly conflicts, user is not eligible
    if not state_match:
        return EligibilityCheckResponse(
            scheme=scheme,
            eligible=False,
            reasons=[],
            warnings=warnings,
        )

    # 4. Evaluate against eligibility records (OR logic)
    compatible_records: List[Dict[str, Any]] = [
        elig for elig in elig_records if _is_eligibility_compatible(elig, request)
    ]

    if not compatible_records:
        return EligibilityCheckResponse(
            scheme=scheme,
            eligible=False,
            reasons=[],
            warnings=warnings,
        )

    # 5. User is eligible (matched at least one eligibility record)
    reasons: List[str] = []

    # State match reason
    if request.state and request.state.strip() and state_match:
        states = scheme_data.get("states")
        has_states = False
        if isinstance(states, list):
            has_states = any(bool(st and str(st).strip()) for st in states)
        elif isinstance(states, str):
            has_states = bool(states.strip())
        if has_states:
            reasons.append("User state is supported by the scheme.")

    matching_elig = compatible_records[0]

    # Age
    if request.age is not None:
        min_age = matching_elig.get("min_age")
        max_age = matching_elig.get("max_age")
        if min_age is not None and max_age is not None:
            reasons.append("User age is within the eligible age range.")
        elif min_age is not None:
            reasons.append("User age meets the minimum age requirement.")
        elif max_age is not None:
            reasons.append("User age is below the maximum age requirement.")
        else:
            warnings.append("Age eligibility information is not available.")

    # Gender
    if request.gender and request.gender.strip():
        gender_val = matching_elig.get("gender")
        if gender_val and str(gender_val).strip():
            reasons.append("Gender matches the eligibility requirement.")
        else:
            warnings.append("Gender eligibility information is not available.")

    # Occupation
    if request.occupation and request.occupation.strip():
        occ_val = matching_elig.get("occupation")
        if occ_val and str(occ_val).strip():
            reasons.append("Occupation matches the eligibility requirement.")
        else:
            warnings.append("Occupation eligibility information is not available.")

    # Income
    if request.annual_income is not None:
        inc_min = matching_elig.get("income_min")
        inc_max = matching_elig.get("income_max")
        if inc_min is not None and inc_max is not None:
            reasons.append("Annual income is within the eligible income range.")
        elif inc_max is not None:
            reasons.append("Annual income is below the maximum eligible income.")
        elif inc_min is not None:
            reasons.append("Annual income meets the minimum eligible income.")
        else:
            warnings.append("Income eligibility information is not available.")

    # Caste
    if request.caste_category and request.caste_category.strip():
        caste_val = matching_elig.get("caste_category")
        if caste_val and str(caste_val).strip():
            reasons.append("Caste category matches the eligibility requirement.")
        else:
            warnings.append("Caste category eligibility information is not available.")

    # Education
    if request.education and request.education.strip():
        edu_val = matching_elig.get("education")
        if edu_val and str(edu_val).strip():
            reasons.append("Education matches the eligibility requirement.")
        else:
            warnings.append("Education eligibility information is not available.")

    # Disability
    if request.disability is not None and matching_elig.get("disability_required") is True:
        if request.disability is True:
            reasons.append("User satisfies the disability requirement.")

    # Land
    if request.land_owned is not None and matching_elig.get("land_required") is True:
        if request.land_owned is True:
            reasons.append("User satisfies the land ownership requirement.")

    # Business
    if request.business_exists is not None and matching_elig.get("business_required") is True:
        if request.business_exists is True:
            reasons.append("User satisfies the business requirement.")

    return EligibilityCheckResponse(
        scheme=scheme,
        eligible=True,
        reasons=reasons,
        warnings=warnings,
    )
