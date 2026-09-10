"""Google Places Competitor Intelligence Service for RuralEdge.

Architecture:
  Location (State, District, Village)
        ↓
  Latitude / Longitude Geocoding
        ↓
  Google Places API (Nearby / Text Search)
        ↓
  Nearby Competitors & Haversine Distance
        ↓
  Deterministic Competitor Density Scoring (0-100)
        ↓
  Market Intelligence Output

Design Rules:
  1. API key read ONLY from GOOGLE_MAPS_API_KEY or GOOGLE_PLACES_API_KEY environment variable.
  2. Never expose key to frontend or log files.
  3. Deterministic Category Query Mapping for key rural & MSME sectors.
  4. If category is unknown, use the category string itself as the query.
  5. API Failure Policy:
     - If Google Places API is unavailable (missing key, quota, timeout, network failure), return:
       status="unavailable", competitor_count=None, competition_score=None, message="...".
     - Never return competitor_count=0 on API failure (0 count means search succeeded with 0 results).
"""

import logging
import math
import os
from typing import Dict, List, Optional, Tuple
import httpx

from app.schemas.business import CompetitorDetail, LocationInput, MarketInfo

logger = logging.getLogger(__name__)

# Deterministic Business Category Mapping for Google Places Search
CATEGORY_SEARCH_MAP: Dict[str, List[str]] = {
    "dairy": ["dairy shop", "milk shop", "dairy farm"],
    "bakery": ["bakery"],
    "grocery": ["grocery store", "supermarket"],
    "restaurant": ["restaurant"],
    "tailoring": ["tailor"],
    "mobile repair": ["mobile phone repair shop"],
    "pharmacy": ["pharmacy", "medical shop"],
    "poultry": ["poultry farm", "chicken shop"],
    "textile": ["textile shop", "clothing store"],
    "handicraft": ["handicraft shop", "handloom"],
    "furniture": ["furniture store"],
    "auto repair": ["auto repair shop", "garage"],
    "salon": ["beauty salon", "barber shop"],
    "vegetable shop": ["vegetable market", "greengrocer"],
}


def get_google_places_competitor_analysis(
    location: LocationInput,
    business_category: str,
    radius_km: int = 10,
) -> MarketInfo:
    """Perform Google Places competitor search around the given location.

    Args:
        location: LocationInput (state, district, village).
        business_category: Business category (e.g. 'Dairy', 'Poultry').
        radius_km: Search radius in kilometers (default 10).

    Returns:
        MarketInfo object following the normalized schema.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY environment variable is not configured.")
        return MarketInfo(
            status="unavailable",
            source="google_places",
            radius_km=radius_km,
            competitor_count=None,
            competitors=[],
            market_reach_score=None,
            competition_score=None,
            message="Google Places data is currently unavailable.",
        )

    try:
        # Step 1: Geocode location to lat, lng
        lat, lng = _geocode_location(location, api_key)
        if lat is None or lng is None:
            logger.warning(f"Unable to geocode location: {location.model_dump()}")
            return MarketInfo(
                status="unavailable",
                source="google_places",
                radius_km=radius_km,
                competitor_count=None,
                competitors=[],
                market_reach_score=None,
                competition_score=None,
                message="Google Places data is currently unavailable.",
            )

        # Step 2: Query Google Places API
        competitors = _fetch_google_places(
            lat=lat,
            lng=lng,
            business_category=business_category,
            radius_km=radius_km,
            api_key=api_key,
        )

        # Step 3: Compute deterministic density score
        competitor_count = len(competitors)
        competition_score = _calculate_competition_score(competitors, competitor_count)
        market_reach_score = min(100, max(0, 100 - competition_score + 25))

        return MarketInfo(
            status="success",
            source="google_places",
            radius_km=radius_km,
            competitor_count=competitor_count,
            competitors=competitors,
            market_reach_score=market_reach_score,
            competition_score=competition_score,
            message=None,
        )

    except Exception as exc:
        logger.error(f"Google Places API search failed: {exc}")
        return MarketInfo(
            status="unavailable",
            source="google_places",
            radius_km=radius_km,
            competitor_count=None,
            competitors=[],
            market_reach_score=None,
            competition_score=None,
            message="Google Places data is currently unavailable.",
        )


def _geocode_location(
    location: LocationInput,
    api_key: str,
) -> Tuple[Optional[float], Optional[float]]:
    """Geocode address using Google Geocoding API."""
    parts = []
    if location.village and location.village.strip():
        parts.append(location.village.strip())
    if location.district and location.district.strip():
        parts.append(location.district.strip())
    if location.state and location.state.strip():
        parts.append(location.state.strip())
    parts.append("India")

    address_str = ", ".join(parts)
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address_str, "key": api_key}

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                return float(loc["lat"]), float(loc["lng"])

    return None, None


def _fetch_google_places(
    lat: float,
    lng: float,
    business_category: str,
    radius_km: int,
    api_key: str,
) -> List[CompetitorDetail]:
    """Execute Google Places Text Search and return normalized CompetitorDetail objects."""
    cat_clean = business_category.strip().lower()
    search_queries = CATEGORY_SEARCH_MAP.get(cat_clean, [business_category])
    query_str = " OR ".join(search_queries)

    radius_meters = radius_km * 1000
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query_str,
        "location": f"{lat},{lng}",
        "radius": radius_meters,
        "key": api_key,
    }

    competitors: List[CompetitorDetail] = []
    seen_place_ids = set()

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"Google Places API returned status code {resp.status_code}")

        data = resp.json()
        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Google Places API returned status '{status}'")

        results = data.get("results", [])
        for place in results:
            place_id = place.get("place_id")
            if place_id and place_id in seen_place_ids:
                continue
            if place_id:
                seen_place_ids.add(place_id)

            geom = place.get("geometry", {}).get("location", {})
            place_lat = geom.get("lat")
            place_lng = geom.get("lng")

            dist_km: Optional[float] = None
            if place_lat is not None and place_lng is not None:
                dist_km = haversine_distance(lat, lng, float(place_lat), float(place_lng))
                dist_km = round(dist_km, 2)
                if dist_km > radius_km * 1.5:
                    continue

            name = place.get("name", "Unknown Business")
            address = place.get("formatted_address") or place.get("vicinity")
            rating = place.get("rating")
            user_ratings_total = place.get("user_ratings_total")

            types = place.get("types", [])
            primary_cat = business_category
            if types:
                primary_cat = types[0].replace("_", " ").title()

            competitor = CompetitorDetail(
                name=name,
                category=primary_cat,
                address=address,
                latitude=float(place_lat) if place_lat is not None else None,
                longitude=float(place_lng) if place_lng is not None else None,
                distance_km=dist_km,
                rating=float(rating) if rating is not None else None,
                user_ratings_total=int(user_ratings_total) if user_ratings_total is not None else None,
                source="google_places",
            )
            competitors.append(competitor)

    # Sort competitors by nearest distance
    competitors.sort(key=lambda c: c.distance_km if c.distance_km is not None else 999.0)
    return competitors


def _calculate_competition_score(
    competitors: List[CompetitorDetail],
    competitor_count: int,
) -> int:
    """Calculate deterministic competition feasibility score from 0-100.

    SIH-Demo Documented Scoring Formula:
      - Count-based Base Feasibility Score:
          0 competitors        -> 95 (High opportunity, minimal competition)
          1-2 competitors      -> 85 (Solid opportunity, low competition)
          3-5 competitors      -> 70 (Moderate competition)
          6-10 competitors     -> 55 (Established competition)
          > 10 competitors     -> 35 (Saturated market)

      - Proximity Penalty:
          Deduct 3 points for each competitor located within 3 km of target site
          (capped at max 15 points deduction).

      - Score Clamping: Clamped to range [0, 100].
    """
    if competitor_count == 0:
        return 95

    if competitor_count <= 2:
        base = 85
    elif competitor_count <= 5:
        base = 70
    elif competitor_count <= 10:
        base = 55
    else:
        base = 35

    close_competitors = sum(
        1 for c in competitors if c.distance_km is not None and c.distance_km <= 3.0
    )
    proximity_penalty = min(15, close_competitors * 3)

    final_score = base - proximity_penalty
    return max(0, min(100, final_score))


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate geodesic distance between two points on Earth in kilometers using Haversine formula."""
    r = 6371.0  # Radius of earth in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c
