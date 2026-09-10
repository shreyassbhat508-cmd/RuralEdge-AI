"""Competitor Intelligence Service for RuralEdge.

Architecture:
  User Location (State, District, Village)
        ↓
  Primary: Google Places API (if API key present)
        ↓
  Is Google Places Available / Successful?
   ├── YES ──> Return Google Places Competitor Data (source: "google_places")
   └── NO  ──> Fallback: OpenStreetMap Overpass API (source: "osm")
                  ↓
               Is OSM Available / Successful?
                ├── YES ──> Return OSM Competitor Data (source: "osm")
                └── NO  ──> Fallback: Unavailable (source: "fallback_unavailable", status: "unavailable")

Design Rules:
  1. Primary: Google Places API using GOOGLE_PLACES_API_KEY / GOOGLE_MAPS_API_KEY.
  2. Fallback: OpenStreetMap Overpass API (no API key required).
  3. Support configurable search radius (default 10 km).
  4. Search using category-specific OSM tags and Places queries.
  5. Never crash /api/business/analyze if APIs fail or key is missing.
  6. Never fabricate competitor counts or fake data.
  7. In-memory caching with TTL to prevent redundant network calls.
"""

import logging
import math
import os
import time
from typing import Dict, List, Optional, Tuple, Union
import httpx

from app.schemas.business import CompetitorDetail, LocationInput, MarketInfo

logger = logging.getLogger(__name__)

# Cache configuration: Dict[cache_key, (timestamp, MarketInfo)]
_CACHE: Dict[str, Tuple[float, MarketInfo]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache

# Business category query mapping for Google Places API
GOOGLE_QUERY_MAP: Dict[str, str] = {
    "dairy": "dairy farm milk parlor dairy store milk processing",
    "poultry": "poultry farm chicken shop egg dealer",
    "agriculture": "agri store seed fertilizer farm equipment supplier",
    "agri-tech": "agritech agriculture equipment solar pump supplier",
    "food processing": "food processing unit flour mill spice mill agro mill",
    "horticulture": "nursery plant nursery fruit seller wholesale vegetable market",
    "fisheries": "fish farm seafood seller aquaculture dealer",
    "goat farming": "livestock market goat farm animal feed dealer",
    "organic farming": "organic store organic farm produce dealer",
    "retail": "supermarket grocery store general store Kirana",
    "grocery": "grocery store Kirana supermarket",
    "tailoring": "garment shop textile shop tailoring unit",
    "repair shop": "auto repair garage workshop agricultural equipment repair",
}

# Business category tag mapping for OpenStreetMap Overpass API (key, value)
OSM_TAG_MAP: Dict[str, List[Tuple[str, str]]] = {
    "dairy": [("shop", "dairy"), ("craft", "dairy"), ("shop", "milk")],
    "poultry": [("shop", "butcher"), ("shop", "poultry")],
    "agriculture": [("shop", "farm"), ("shop", "agrarian"), ("shop", "garden_centre")],
    "agri-tech": [("shop", "farm"), ("shop", "agrarian"), ("industrial", "machinery")],
    "food processing": [("craft", "bakery"), ("industrial", "factory"), ("man_made", "works")],
    "horticulture": [("shop", "florist"), ("shop", "garden_centre"), ("shop", "greengrocer")],
    "fisheries": [("shop", "seafood"), ("shop", "fish")],
    "goat farming": [("shop", "farm"), ("livestock", "goat")],
    "organic farming": [("shop", "organic"), ("shop", "farm")],
    "retail": [("shop", "supermarket"), ("shop", "convenience"), ("shop", "general"), ("shop", "grocery")],
    "grocery": [("shop", "grocery"), ("shop", "convenience"), ("shop", "supermarket")],
    "tailoring": [("shop", "clothes"), ("shop", "tailor"), ("craft", "tailor")],
    "repair shop": [("shop", "car_repair"), ("shop", "motorcycle_repair"), ("craft", "car_repair")],
}


def get_competitor_analysis(
    location: LocationInput,
    business_category: str,
    radius_km: int = 10,
) -> MarketInfo:
    """Fetch competitor intelligence for a given location and category.

    Order of evaluation:
      1. Return cached result if fresh.
      2. Preferred: Google Places API (if API key present).
      3. Fallback: OpenStreetMap Overpass API (no API key required).
      4. Final Fallback: status='unavailable' (no crash, no fake data).
    """
    cache_key = _build_cache_key(location, business_category, radius_km)
    cached_result = _get_from_cache(cache_key)
    if cached_result:
        logger.info(f"Returning cached competitor analysis for key: '{cache_key}'")
        return cached_result

    # --- 1. Primary Provider: Google Places API ---
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key:
        try:
            logger.info("Attempting Google Places API competitor analysis...")
            lat, lng = _geocode_google(location, api_key)
            if lat is not None and lng is not None:
                competitors = _fetch_google_places(
                    lat=lat,
                    lng=lng,
                    business_category=business_category,
                    radius_km=radius_km,
                    api_key=api_key,
                )
                competitor_count = len(competitors)
                competition_score = _calculate_competition_score(competitors, competitor_count, radius_km)
                market_reach_score = min(100, max(0, 100 - competition_score + 30))

                status = "success" if competitor_count > 0 else "no_results"
                result = MarketInfo(
                    source="google_places",
                    status=status,
                    radius_km=radius_km,
                    competitor_count=competitor_count,
                    competitors=competitors,
                    market_reach_score=market_reach_score,
                    competition_score=competition_score,
                )
                _save_to_cache(cache_key, result)
                return result
        except Exception as exc:
            logger.warning(f"Google Places API failed ({exc}). Falling back to OpenStreetMap Overpass API.")

    # --- 2. Secondary Provider Fallback: OpenStreetMap Overpass API ---
    try:
        logger.info("Attempting OpenStreetMap Overpass API competitor analysis...")
        address_str = _build_address_string(location)
        lat, lng = _geocode_nominatim(address_str)
        if lat is not None and lng is not None:
            competitors = _fetch_overpass_places(
                lat=lat,
                lng=lng,
                business_category=business_category,
                radius_km=radius_km,
            )
            competitor_count = len(competitors)
            competition_score = _calculate_competition_score(competitors, competitor_count, radius_km)
            market_reach_score = min(100, max(0, 100 - competition_score + 30))

            status = "success" if competitor_count > 0 else "no_results"
            result = MarketInfo(
                source="osm",
                status=status,
                radius_km=radius_km,
                competitor_count=competitor_count,
                competitors=competitors,
                market_reach_score=market_reach_score,
                competition_score=competition_score,
            )
            _save_to_cache(cache_key, result)
            return result
    except Exception as exc:
        logger.warning(f"OpenStreetMap Overpass API failed ({exc}).")

    # --- 3. Final Fallback: Unavailable status ---
    logger.info("Both Google Places and OSM unavailable. Returning status='unavailable'.")
    fallback = MarketInfo(
        source="fallback_unavailable",
        status="unavailable",
        radius_km=radius_km,
        competitor_count=0,
        competitors=[],
        market_reach_score=0,
        competition_score=70,
    )
    return fallback


def _build_address_string(location: LocationInput) -> str:
    parts = []
    if location.village and location.village.strip():
        parts.append(location.village.strip())
    if location.district and location.district.strip():
        parts.append(location.district.strip())
    if location.state and location.state.strip():
        parts.append(location.state.strip())
    parts.append("India")
    return ", ".join(parts)


def _geocode_google(
    location: LocationInput,
    api_key: str,
) -> Tuple[Optional[float], Optional[float]]:
    address_str = _build_address_string(location)
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address_str, "key": api_key}

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                return float(loc["lat"]), float(loc["lng"])

    return _geocode_nominatim(address_str)


def _geocode_nominatim(address_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Free geocoder using OpenStreetMap Nominatim."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "RuralEdge-AI/1.0"}
        params = {"q": address_str, "format": "json", "limit": 1}

        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        logger.debug(f"Nominatim geocoding failed: {e}")

    return None, None


def _fetch_google_places(
    lat: float,
    lng: float,
    business_category: str,
    radius_km: int,
    api_key: str,
) -> List[CompetitorDetail]:
    """Query Google Places API text search."""
    category_clean = business_category.strip().lower()
    search_query = GOOGLE_QUERY_MAP.get(category_clean, f"{business_category} in region")

    radius_meters = radius_km * 1000
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": search_query,
        "location": f"{lat},{lng}",
        "radius": radius_meters,
        "key": api_key,
    }

    competitors: List[CompetitorDetail] = []

    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, params=params)
        if resp.status_code != 200:
            logger.warning(f"Google Places HTTP status {resp.status_code}")
            return competitors

        data = resp.json()
        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            logger.warning(f"Google Places status: {data.get('status')}")
            return competitors

        results = data.get("results", [])
        for place in results:
            place_lat = place.get("geometry", {}).get("location", {}).get("lat")
            place_lng = place.get("geometry", {}).get("location", {}).get("lng")

            dist_km: Optional[float] = None
            if place_lat is not None and place_lng is not None:
                dist_km = _haversine_distance(lat, lng, float(place_lat), float(place_lng))
                dist_km = round(dist_km, 2)
                if dist_km > radius_km * 1.5:
                    continue

            name = place.get("name", "Unknown Competitor")
            address = place.get("formatted_address") or place.get("vicinity")
            rating = place.get("rating")
            user_ratings_total = place.get("user_ratings_total")

            types = place.get("types", [])
            primary_cat = business_category
            if types:
                primary_cat = types[0].replace("_", " ").title()

            competitor = CompetitorDetail(
                name=name,
                address=address,
                category=primary_cat,
                distance_km=dist_km,
                rating=float(rating) if rating is not None else None,
                user_ratings_total=int(user_ratings_total) if user_ratings_total is not None else None,
            )
            competitors.append(competitor)

    competitors.sort(key=lambda c: c.distance_km if c.distance_km is not None else 999.0)
    return competitors


def _fetch_overpass_places(
    lat: float,
    lng: float,
    business_category: str,
    radius_km: int,
) -> List[CompetitorDetail]:
    """Query OpenStreetMap Overpass API interpreter using category-specific tags."""
    radius_meters = radius_km * 1000
    category_clean = business_category.strip().lower()
    tag_pairs = OSM_TAG_MAP.get(category_clean, [("shop", category_clean), ("shop", "yes")])

    statements = []
    for k, v in tag_pairs:
        if v == "yes":
            statements.append(f'node["{k}"](around:{radius_meters},{lat},{lng});')
            statements.append(f'way["{k}"](around:{radius_meters},{lat},{lng});')
        else:
            statements.append(f'node["{k}"="{v}"](around:{radius_meters},{lat},{lng});')
            statements.append(f'way["{k}"="{v}"](around:{radius_meters},{lat},{lng});')

    query_body = "\n".join(statements)
    overpass_ql = f"""[out:json][timeout:15];
(
{query_body}
);
out center;"""

    url = "https://overpass-api.de/api/interpreter"
    headers = {"User-Agent": "RuralEdge-AI/1.0"}
    competitors: List[CompetitorDetail] = []

    with httpx.Client(timeout=15.0) as client:
        resp = client.post(url, data={"data": overpass_ql}, headers=headers)
        if resp.status_code != 200:
            logger.warning(f"Overpass API status {resp.status_code}")
            return competitors

        data = resp.json()
        elements = data.get("elements", [])

        seen_keys = set()

        for elem in elements:
            tags = elem.get("tags", {})
            name = tags.get("name") or tags.get("brand") or tags.get("operator")
            if not name:
                # Omit generic unnamed nodes without specific commercial tags
                shop_tag = tags.get("shop") or tags.get("craft") or tags.get("amenity")
                if not shop_tag:
                    continue
                name = f"{shop_tag.replace('_', ' ').title()} Enterprise"

            elem_type = elem.get("type")
            if elem_type == "node":
                elem_lat = elem.get("lat")
                elem_lng = elem.get("lon")
            else:
                center = elem.get("center", {})
                elem_lat = center.get("lat")
                elem_lng = center.get("lon")

            if elem_lat is None or elem_lng is None:
                continue

            dist_km = _haversine_distance(lat, lng, float(elem_lat), float(elem_lng))
            dist_km = round(dist_km, 2)
            if dist_km > radius_km * 1.5:
                continue

            # Deduplication check by name + rounded lat/lng
            dedup_key = f"{name.lower().strip()}:{round(float(elem_lat), 3)}:{round(float(elem_lng), 3)}"
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            addr_parts = [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:suburb") or tags.get("addr:village"),
                tags.get("addr:city") or tags.get("addr:district"),
            ]
            address = ", ".join([p for p in addr_parts if p]) or tags.get("addr:full") or None

            cat_tag = tags.get("shop") or tags.get("craft") or tags.get("amenity") or business_category
            category_display = cat_tag.replace("_", " ").title()

            competitor = CompetitorDetail(
                name=name,
                address=address,
                category=category_display,
                distance_km=dist_km,
                rating=None,  # OSM doesn't store user ratings
                user_ratings_total=None,
            )
            competitors.append(competitor)

    competitors.sort(key=lambda c: c.distance_km if c.distance_km is not None else 999.0)
    return competitors


def _calculate_competition_score(
    competitors: List[CompetitorDetail],
    competitor_count: int,
    radius_km: int,
) -> int:
    """Calculate competitor density score from 0-100."""
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

    close_competitors = sum(1 for c in competitors if c.distance_km is not None and c.distance_km <= 3.0)
    proximity_penalty = min(20, close_competitors * 4)

    final_score = base - proximity_penalty
    return max(0, min(100, final_score))


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km using Haversine formula."""
    r = 6371.0
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


def _build_cache_key(location: LocationInput, business_category: str, radius_km: int) -> str:
    loc_part = f"{location.state}_{location.district}_{location.village or ''}".lower().strip()
    cat_part = business_category.lower().strip()
    return f"{loc_part}:{cat_part}:{radius_km}"


def _get_from_cache(cache_key: str) -> Optional[MarketInfo]:
    if cache_key in _CACHE:
        ts, data = _CACHE[cache_key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            return data
        else:
            del _CACHE[cache_key]
    return None


def _save_to_cache(cache_key: str, data: MarketInfo) -> None:
    _CACHE[cache_key] = (time.time(), data)
