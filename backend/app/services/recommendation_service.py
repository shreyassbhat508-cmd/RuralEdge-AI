import logging
from typing import Any, Dict, List, Optional, cast
from app.database import supabase
from app.schemas.recommendation import RecommendationRequest

logger = logging.getLogger(__name__)


def _is_state_match(scheme_states: Any, user_state: Optional[str]) -> bool:
    if not user_state or not user_state.strip():
        return True

    u_state = user_state.strip().lower()

    if not scheme_states:
        return True

    if isinstance(scheme_states, list):
        valid_states = [str(st).strip().lower() for st in scheme_states if st and str(st).strip()]
        if not valid_states:
            return True

        for st_str in valid_states:
            if st_str in ["all", "all india", "national"] or st_str == u_state or u_state in st_str or st_str in u_state:
                return True
        return False

    if isinstance(scheme_states, str):
        st_str = scheme_states.strip().lower()
        if not st_str:
            return True
        if st_str in ["all", "all india", "national"] or st_str == u_state or u_state in st_str or st_str in u_state:
            return True
        return False

    return True


def _is_eligibility_compatible(elig: Dict[str, Any], request: RecommendationRequest) -> bool:
    # Age checks
    min_age = elig.get("min_age")
    if min_age is not None and request.age is not None:
        if request.age < float(min_age):
            return False

    max_age = elig.get("max_age")
    if max_age is not None and request.age is not None:
        if request.age > float(max_age):
            return False

    # Gender check
    gender_val = elig.get("gender")
    if gender_val and request.gender and request.gender.strip():
        e_gender = str(gender_val).strip().lower()
        u_gender = request.gender.strip().lower()
        if e_gender not in ["all", "any", "both", "all gender", "all genders"]:
            g_map = {"m": "male", "f": "female", "man": "male", "woman": "female"}
            e_norm = g_map.get(e_gender, e_gender)
            u_norm = g_map.get(u_gender, u_gender)
            if e_norm != u_norm:
                e_words = set(e_norm.split())
                u_words = set(u_norm.split())
                if not e_words.intersection(u_words):
                    return False

    # Income checks
    income_min = elig.get("income_min")
    if income_min is not None and request.annual_income is not None:
        if request.annual_income < float(income_min):
            return False

    income_max = elig.get("income_max")
    if income_max is not None and request.annual_income is not None:
        if request.annual_income > float(income_max):
            return False

    # Caste check
    caste_val = elig.get("caste_category")
    if caste_val and request.caste_category and request.caste_category.strip():
        e_caste = str(caste_val).strip().lower()
        u_caste = request.caste_category.strip().lower()
        if e_caste not in ["all", "any", "general"]:
            if e_caste != u_caste and e_caste not in u_caste and u_caste not in e_caste:
                return False

    # Occupation check
    occ_val = elig.get("occupation")
    if occ_val and request.occupation and request.occupation.strip():
        e_occ = str(occ_val).strip().lower()
        u_occ = request.occupation.strip().lower()
        if e_occ not in ["all", "any", "all occupations", "any occupation"]:
            u_words = set(u_occ.split())
            e_words = set(e_occ.split())
            if not u_words.intersection(e_words) and u_occ not in e_occ and e_occ not in u_occ:
                return False

    # Education check
    edu_val = elig.get("education")
    if edu_val and request.education and request.education.strip():
        e_edu = str(edu_val).strip().lower()
        u_edu = request.education.strip().lower()
        if e_edu not in ["all", "any", "none", "not required"]:
            if u_edu not in e_edu and e_edu not in u_edu:
                return False

    # Disability check
    if elig.get("disability_required") is True:
        if request.disability is False:
            return False

    # Land check
    if elig.get("land_required") is True:
        if request.land_owned is False:
            return False

    # Business check
    if elig.get("business_required") is True:
        if request.business_exists is False:
            return False

    return True


def _evaluate_scheme_recommendation(
    scheme: Dict[str, Any],
    scheme_elig_list: List[Dict[str, Any]],
    request: RecommendationRequest,
) -> Optional[Dict[str, Any]]:
    # State compatibility check
    if not _is_state_match(scheme.get("states"), request.state):
        return None

    state_score = 10
    location_reasons: List[str] = []
    location_warnings: List[str] = []

    if request.state and request.state.strip():
        states = scheme.get("states")
        has_states = False
        if isinstance(states, list):
            has_states = any(bool(st and str(st).strip()) for st in states)
        elif isinstance(states, str):
            has_states = bool(states.strip())

        if has_states:
            state_score = 20
            location_reasons.append("User state is supported by the scheme.")
        else:
            state_score = 10
            location_warnings.append("State-specific eligibility information is not available.")
    else:
        state_score = 10

    if request.district and request.district.strip():
        location_warnings.append("District-specific eligibility information is not available.")

    # Handle zero eligibility records case
    if not scheme_elig_list:
        total_score = min(100, state_score + 20)
        all_warnings = location_warnings + ["Eligibility information is not available for this scheme."]
        return {
            "scheme": scheme,
            "eligibility": [],
            "match_reasons": location_reasons if location_reasons else ["Scheme has general availability."],
            "match_score": total_score,
            "warnings": all_warnings,
        }

    # Evaluate each compatible eligibility record (OR logic)
    compatible_evaluations: List[Dict[str, Any]] = []

    for elig in scheme_elig_list:
        if not _is_eligibility_compatible(elig, request):
            continue

        record_score = 0
        reasons: List[str] = list(location_reasons)
        warnings: List[str] = list(location_warnings)

        # Age
        min_age = elig.get("min_age")
        max_age = elig.get("max_age")
        if min_age is not None or max_age is not None:
            if request.age is not None:
                record_score += 15
                if min_age is not None and max_age is not None:
                    reasons.append("User age is within the eligible age range.")
                elif min_age is not None:
                    reasons.append("User age meets the minimum age requirement.")
                elif max_age is not None:
                    reasons.append("User age is below the maximum age requirement.")
            else:
                record_score += 5
                warnings.append("Age was not provided; age criteria could not be fully verified.")
        else:
            record_score += 5
            if request.age is not None:
                warnings.append("Age eligibility information is not available.")

        # Gender
        gender_val = elig.get("gender")
        if gender_val and str(gender_val).strip() and str(gender_val).strip().lower() not in ["all", "any", "both", "all gender", "all genders"]:
            if request.gender and request.gender.strip():
                record_score += 15
                reasons.append("Gender matches the eligibility requirement.")
            else:
                record_score += 5
                warnings.append("Gender was not provided; gender criteria could not be fully verified.")
        else:
            record_score += 5
            if request.gender and request.gender.strip() and not (gender_val and str(gender_val).strip()):
                warnings.append("Gender eligibility information is not available.")

        # Occupation
        occ_val = elig.get("occupation")
        if occ_val and str(occ_val).strip() and str(occ_val).strip().lower() not in ["all", "any", "all occupations", "any occupation"]:
            if request.occupation and request.occupation.strip():
                record_score += 15
                reasons.append("Occupation matches the eligibility requirement.")
            else:
                record_score += 5
                warnings.append("Occupation was not provided; occupation criteria could not be fully verified.")
        else:
            record_score += 5
            if request.occupation and request.occupation.strip() and not (occ_val and str(occ_val).strip()):
                warnings.append("Occupation eligibility information is not available.")

        # Income
        inc_min = elig.get("income_min")
        inc_max = elig.get("income_max")
        if inc_min is not None or inc_max is not None:
            if request.annual_income is not None:
                record_score += 15
                if inc_min is not None and inc_max is not None:
                    reasons.append("Annual income is within the eligible income range.")
                elif inc_max is not None:
                    reasons.append("Annual income is below the maximum eligible income.")
                elif inc_min is not None:
                    reasons.append("Annual income meets the minimum eligible income.")
            else:
                record_score += 5
                warnings.append("Annual income was not provided; income criteria could not be fully verified.")
        else:
            record_score += 5
            if request.annual_income is not None:
                warnings.append("Income eligibility information is not available.")

        # Caste
        caste_val = elig.get("caste_category")
        if caste_val and str(caste_val).strip() and str(caste_val).strip().lower() not in ["all", "any", "general"]:
            if request.caste_category and request.caste_category.strip():
                record_score += 10
                reasons.append("Caste category matches the eligibility requirement.")
            else:
                record_score += 5
                warnings.append("Caste category was not provided; caste criteria could not be fully verified.")
        else:
            record_score += 5
            if request.caste_category and request.caste_category.strip() and not (caste_val and str(caste_val).strip()):
                warnings.append("Caste category eligibility information is not available.")

        # Education
        edu_val = elig.get("education")
        if edu_val and str(edu_val).strip() and str(edu_val).strip().lower() not in ["all", "any", "none", "not required"]:
            if request.education and request.education.strip():
                record_score += 10
                reasons.append("Education matches the eligibility requirement.")
            else:
                record_score += 5
                warnings.append("Education qualification was not provided; education criteria could not be fully verified.")
        else:
            record_score += 5
            if request.education and request.education.strip() and not (edu_val and str(edu_val).strip()):
                warnings.append("Education eligibility information is not available.")

        # Disability
        if elig.get("disability_required") is True:
            if request.disability is True:
                record_score += 10
                reasons.append("User satisfies the disability requirement.")
            elif request.disability is None:
                record_score += 5
                warnings.append("Disability status was not provided; disability requirement could not be fully verified.")

        # Land
        if elig.get("land_required") is True:
            if request.land_owned is True:
                record_score += 10
                reasons.append("User satisfies the land ownership requirement.")
            elif request.land_owned is None:
                record_score += 5
                warnings.append("Land ownership status was not provided; land requirement could not be fully verified.")

        # Business
        if elig.get("business_required") is True:
            if request.business_exists is True:
                record_score += 10
                reasons.append("User satisfies the business requirement.")
            elif request.business_exists is None:
                record_score += 5
                warnings.append("Business status was not provided; business requirement could not be fully verified.")

        total_score = min(100, state_score + record_score)

        compatible_evaluations.append({
            "score": total_score,
            "reasons": reasons,
            "warnings": warnings,
        })

    if not compatible_evaluations:
        return None

    best_eval = max(compatible_evaluations, key=lambda x: x["score"])

    return {
        "scheme": scheme,
        "eligibility": scheme_elig_list,
        "match_reasons": best_eval["reasons"],
        "match_score": best_eval["score"],
        "warnings": best_eval["warnings"],
    }


def get_recommendations(request: RecommendationRequest) -> List[Dict[str, Any]]:
    """
    Deterministically find potential matching schemes for a user without using AI.
    Performs READ-ONLY queries on schemes, scheme_eligibility, and scheme_benefits.
    Returns matched schemes with transparent match_reasons, deterministic match_scores, and warnings.
    """
    try:
        # 1. Fetch schemes
        schemes_res = supabase.table("schemes").select("*").execute()
        raw_schemes = schemes_res.data
        schemes_data: List[Dict[str, Any]] = cast(List[Dict[str, Any]], raw_schemes) if isinstance(raw_schemes, list) else []

        if not schemes_data:
            return []

        # 2. Fetch eligibility records
        elig_res = supabase.table("scheme_eligibility").select("*").execute()
        raw_elig = elig_res.data
        elig_data: List[Dict[str, Any]] = cast(List[Dict[str, Any]], raw_elig) if isinstance(raw_elig, list) else []

        elig_by_scheme: Dict[str, List[Dict[str, Any]]] = {}
        for row in elig_data:
            if isinstance(row, dict):
                sid = row.get("scheme_id")
                if isinstance(sid, str) and sid:
                    elig_by_scheme.setdefault(sid, []).append(row)

        # 3. Fetch benefits records
        ben_res = supabase.table("scheme_benefits").select("*").execute()
        raw_ben = ben_res.data
        ben_data: List[Dict[str, Any]] = cast(List[Dict[str, Any]], raw_ben) if isinstance(raw_ben, list) else []

        ben_by_scheme: Dict[str, List[Dict[str, Any]]] = {}
        for row in ben_data:
            if isinstance(row, dict):
                sid = row.get("scheme_id")
                if isinstance(sid, str) and sid:
                    ben_by_scheme.setdefault(sid, []).append(row)

        # 4. Perform deterministic matching and score calculation
        recommendations: List[Dict[str, Any]] = []

        for scheme in schemes_data:
            if not isinstance(scheme, dict):
                continue
            scheme_id = scheme.get("id")
            if not isinstance(scheme_id, str) or not scheme_id:
                continue

            eval_res = _evaluate_scheme_recommendation(
                scheme,
                elig_by_scheme.get(scheme_id, []),
                request,
            )

            if eval_res is not None:
                eval_res["benefits"] = ben_by_scheme.get(scheme_id, [])
                recommendations.append(eval_res)

        # Sort recommendations by match_score in descending order
        recommendations.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        return recommendations

    except Exception as e:
        logger.error(f"Error computing recommendations from Supabase: {str(e)}")
        raise RuntimeError("Failed to compute scheme recommendations from database") from e

