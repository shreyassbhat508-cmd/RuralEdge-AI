# RuralEdge Backend API Documentation

## Overview & System Architecture

The **RuralEdge Backend** provides a high-performance, read-only RESTful API built with **FastAPI** and powered by **Supabase PostgreSQL**.

### Key Architectural Declarations:
- **Data Source**: Supabase PostgreSQL database serves as the single source of truth.
- **Read-Only Operations**: All backend database operations are strictly **READ-ONLY** (`SELECT`). The backend does not insert, update, delete, or alter any database table or schema.
- **Ingestion Decoupling**: Government scheme data ingestion and raw document scraping are performed asynchronously by separate ingestion pipelines.
- **Frontend Integration**: The RuralEdge frontend consumes these standardized RESTful endpoints.
- **Zero Schema Alteration**: No database schema, migration, or table structure is recreated or mutated by this backend service.

---

## Standardized Error Response Contract

All non-2xx HTTP responses follow a consistent, predictable JSON structure:

### 1. Standard Error Response (`HTTP 400`, `404`, `413`, `500`, `503`)
```json
{
  "success": false,
  "error": {
    "code": "SCHEME_NOT_FOUND",
    "message": "Scheme not found"
  }
}
```

### 2. Request Validation Error Response (`HTTP 422`)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "state",
        "message": "String should have at most 100 characters",
        "type": "string_too_long"
      }
    ]
  }
}
```

---

## Summary Table of Endpoints

| Tag | Method | Endpoint Path | Purpose | Important HTTP Codes |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/health` | Application status & Supabase connectivity check | `200`, `503` |
| **Schemes** | `GET` | `/api/schemes` | Paginated schemes list with filtering & sorting | `200`, `400`, `422` |
| **Schemes** | `GET` | `/api/schemes/search` | Full-text scheme search | `200`, `422`, `500` |
| **Schemes** | `GET` | `/api/schemes/{scheme_id}` | Retrieve single scheme by UUID | `200`, `404`, `422` |
| **Schemes** | `GET` | `/api/schemes/{scheme_id}/details` | Complete aggregated scheme details | `200`, `404`, `422` |
| **Eligibility** | `GET` | `/api/schemes/{scheme_id}/eligibility` | Scheme eligibility criteria records | `200`, `422`, `500` |
| **Benefits** | `GET` | `/api/schemes/{scheme_id}/benefits` | Scheme benefit records | `200`, `422`, `500` |
| **Eligibility** | `POST` | `/api/schemes/{scheme_id}/eligibility-check` | Check user profile against scheme criteria | `200`, `404`, `422` |
| **Recommendations** | `POST` | `/api/recommendations` | Deterministic scheme matching (No AI) | `200`, `422`, `500` |
| **Loan Calculator** | `POST` | `/api/loan-calculator` | Standalone margin & loan repayment calculator | `200`, `400`, `422` |
| **Loan Calculator** | `POST` | `/api/loan-calculator/scheme/{scheme_id}` | Scheme-based loan financial calculator | `200`, `400`, `404`, `422` |
| **Locations** | `GET` | `/api/locations` | Location records (state, district, taluk, village) | `200`, `422`, `500` |
| **Sources** | `GET` | `/api/sources` | Government data sources | `200`, `422`, `500` |
| **Ingestion** | `GET` | `/api/ingestion` | Ingestion pipeline run logs | `200`, `422`, `500` |
| **Documents** | `GET` | `/api/documents` | Scraped raw government documents | `200`, `422`, `500` |
| **AI Assistant** | `POST` | `/api/ai/chat` | Safe Gemini-powered scheme explainer | `200`, `404`, `422`, `503` |

---

## Detailed Endpoint Specifications

### 1. Health API

#### `GET /api/health`
- **Purpose**: Verifies that the FastAPI application is running and performs a lightweight read-only connectivity check against Supabase.
- **Request Parameters**: None.
- **Successful Response (`200 OK`)**:
  ```json
  {
    "status": "ok",
    "service": "RuralEdge Backend",
    "database": "connected"
  }
  ```
- **Error Response (`503 Service Unavailable`)**:
  ```json
  {
    "status": "degraded",
    "service": "RuralEdge Backend",
    "database": "unavailable"
  }
  ```

---

### 2. Schemes API

#### `GET /api/schemes`
- **Purpose**: Retrieves a paginated list of schemes with optional filtering and sorting.
- **Query Parameters**:
  - `state` *(Optional, string, max 100 chars)*: Filter by supported state.
  - `ministry` *(Optional, string, max 150 chars)*: Filter by ministry name.
  - `department` *(Optional, string, max 150 chars)*: Filter by department name.
  - `scheme_type` *(Optional, string, max 100 chars)*: Filter by scheme type (e.g. `Central`, `State`).
  - `status` *(Optional, string, max 50 chars)*: Filter by status (e.g. `active`).
  - `sort_by` *(Optional, default `"name"`)*: Sort field (`name`, `launch_date`, `created_at`).
  - `sort_order` *(Optional, default `"asc"`)*: Sort order (`asc`, `desc`).
  - `page` *(Optional, int, >= 1, default `1`)*: Page number.
  - `limit` *(Optional, int, 1 to 100, default `10`)*: Page size.
- **Successful Response (`200 OK`)**:
  ```json
  {
    "items": [...],
    "page": 1,
    "limit": 10,
    "total": 25,
    "total_pages": 3
  }
  ```
- **Important Error Responses**:
  - `400 Bad Request`: Invalid `page` (< 1), `limit` (< 1 or > 100), or invalid `sort_by` / `sort_order`.

#### `GET /api/schemes/search`
- **Purpose**: Performs case-insensitive text search across scheme fields (name, short_name, description, ministry, department).
- **Query Parameters**:
  - `query` *(Optional, string, max 200 chars)*: Search keyword.
  - `state` *(Optional, string, max 100 chars)*: Filter by state.
  - `scheme_type` *(Optional, string, max 100 chars)*: Filter by scheme type.
  - `status` *(Optional, string, max 50 chars)*: Filter by status.
  - `ministry` *(Optional, string, max 150 chars)*: Filter by ministry.
- **Successful Response (`200 OK`)**: `List[SchemeResponse]`

#### `GET /api/schemes/{scheme_id}`
- **Purpose**: Retrieves a single scheme record by its UUID.
- **Path Parameters**:
  - `scheme_id` *(Required, UUID)*: Scheme UUID.
- **Important Error Responses**:
  - `404 Not Found`: Scheme ID does not exist (`SCHEME_NOT_FOUND`).
  - `422 Unprocessable`: Invalid UUID format (`VALIDATION_ERROR`).

#### `GET /api/schemes/{scheme_id}/details`
- **Purpose**: Retrieves complete aggregated scheme details including scheme metadata, eligibility criteria, benefit records, and source details.
- **Path Parameters**:
  - `scheme_id` *(Required, UUID)*: Scheme UUID.
- **Successful Response (`200 OK`)**:
  ```json
  {
    "scheme": {...},
    "eligibility": [...],
    "benefits": [...],
    "source": {...}
  }
  ```

---

### 3. Scheme Eligibility & Benefits APIs

#### `GET /api/schemes/{scheme_id}/eligibility`
- **Purpose**: Retrieves eligibility criteria records for a specific scheme.
- **Path Parameters**: `scheme_id` *(Required, UUID)*
- **Response**: `List[EligibilityResponse]`

#### `GET /api/schemes/{scheme_id}/benefits`
- **Purpose**: Retrieves financial and non-financial benefit records for a specific scheme.
- **Path Parameters**: `scheme_id` *(Required, UUID)*
- **Response**: `List[BenefitResponse]`

#### `POST /api/schemes/{scheme_id}/eligibility-check`
- **Purpose**: Evaluates a user profile (`RecommendationRequest`) against a specific scheme's eligibility records.
- **Path Parameters**: `scheme_id` *(Required, UUID)*
- **Request Body**: `RecommendationRequest` (all fields optional)
- **Successful Response (`200 OK`)**:
  ```json
  {
    "scheme": {...},
    "eligible": true,
    "reasons": [
      "Gender matches the eligibility requirement.",
      "Occupation matches the eligibility requirement."
    ],
    "warnings": []
  }
  ```

---

### 4. Recommendations API

#### `POST /api/recommendations`
- **Purpose**: Deterministically evaluates and recommends matching government schemes based on user location (`state`, `district`), demographics (`age`, `gender`, `caste_category`), socio-economic factors (`occupation`, `annual_income`, `education`), and asset/capability status (`disability`, `land_owned`, `business_exists`) without AI/LLM calls.
- **Scoring & Matching Rules**:
  - **Deterministic Score Range**: `0` to `100` points based on verified location match, age, gender, occupation, income, caste, education, and asset requirements.
  - **OR Logic**: Multi-record eligibility criteria per scheme are evaluated as alternative eligibility condition sets. A user is eligible if they satisfy at least one eligibility record.
  - **Missing User / DB Data Handling**: Unspecified database fields or unprovided user fields are not treated as hard failures. Instead, partial points and transparent `warnings` are issued.
  - **Location Handling**: Scheme `states` are checked if present; missing scheme state constraints produce state-unavailability warnings without rejecting the scheme. District-level queries add district-unavailability warnings.
  - **No Eligibility Criteria**: Schemes with 0 eligibility records return a base score with warning `"Eligibility information is not available for this scheme."`
- **Request Body**:
  ```json
  {
    "state": "Karnataka",
    "district": "Bengaluru",
    "age": 25,
    "gender": "female",
    "occupation": "farmer",
    "annual_income": 150000,
    "caste_category": "SC",
    "education": "graduate",
    "disability": false,
    "land_owned": true,
    "business_exists": false
  }
  ```
- **Successful Response (`200 OK`)**: `List[SchemeRecommendation]` containing `scheme`, `eligibility`, `benefits`, `match_reasons`, deterministic `match_score` (0 to 100), and `warnings`.
  ```json
  [
    {
      "scheme": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Pradhan Mantri Kisan Samman Nidhi",
        "short_name": "PM-KISAN",
        "states": ["Karnataka", "Maharashtra"]
      },
      "eligibility": [
        {
          "id": "elig-1",
          "scheme_id": "123e4567-e89b-12d3-a456-426614174000",
          "occupation": "farmer",
          "land_required": true
        }
      ],
      "benefits": [],
      "match_reasons": [
        "User state is supported by the scheme.",
        "Occupation matches the eligibility requirement.",
        "User satisfies the land ownership requirement."
      ],
      "match_score": 85,
      "warnings": [
        "District-specific eligibility information is not available."
      ]
    }
  ]
  ```

---


### 5. Loan Calculator APIs

#### `POST /api/loan-calculator`
- **Purpose**: Standalone financial calculator estimating beneficiary margin money, loan amount, simple interest, total repayment, and approximate monthly payment.
- **Request Body**:
  ```json
  {
    "project_cost": 1000000,
    "margin_percentage": 10,
    "annual_interest_rate": 6,
    "repayment_period_months": 60,
    "moratorium_months": 6
  }
  ```
- **Field Constraints**:
  - `project_cost`: `gt=0, le=100_000_000`
  - `margin_percentage`: `ge=0, le=100`
  - `annual_interest_rate`: `ge=0, le=100`
  - `repayment_period_months`: `gt=0, le=600`
  - `moratorium_months`: `ge=0, <= repayment_period_months`

#### `POST /api/loan-calculator/scheme/{scheme_id}`
- **Purpose**: Scheme-based loan calculator that reads financial parameters (`subsidy_percentage`, `maximum_amount`, `interest_rate`, `repayment_period_months`) directly from Supabase `scheme_benefits`.
- **Path Parameters**: `scheme_id` *(Required, UUID)*
- **Request Body**: `{"project_cost": 1000000, "margin_percentage": 10}`

---

### 6. Supporting Reference APIs

#### `GET /api/locations`
- **Purpose**: Filter locations by state, district, taluk, village, or pincode.

#### `GET /api/sources`
- **Purpose**: Retrieve government data sources.

#### `GET /api/ingestion`
- **Purpose**: Retrieve ingestion pipeline execution logs.

#### `GET /api/documents`
- **Purpose**: Retrieve raw scraped government documents.

---

### 7. AI Assistant API

#### `POST /api/ai/chat`
- **Purpose**: Provides a safe, grounded AI assistant layer powered by Google Gemini to explain government schemes, eligibility requirements, and application procedures in simple, user-friendly language.
- **Safety & Grounding Rules**:
  - **Read-Only Context**: Scheme information is fetched strictly read-only from Supabase PostgreSQL database and provided as trusted context.
  - **No Fabrication**: System instructions strictly prevent inventing eligibility rules, benefit amounts, interest rates, or repayment terms.
  - **No Guaranteed Eligibility**: The AI does not determine official eligibility or process government applications.
  - **Prompt Injection Defense**: User messages are treated strictly as untrusted text and system rules cannot be overridden.
- **Request Body**:
  ```json
  {
    "message": "Can you explain who can apply for this scheme in simple terms?",
    "scheme_id": "123e4567-e89b-12d3-a456-426614174000",
    "language": "English",
    "user_context": {
      "state": "Karnataka",
      "age": 30,
      "gender": "female"
    }
  }
  ```
- **Constraints**:
  - `message`: Required string, max length 2000 characters.
  - `scheme_id`: Optional string, must be a valid UUID when supplied.
- **Successful Response (`200 OK`)**:
  ```json
  {
    "reply": "Janani Suraksha Yojana (JSY) is a government scheme to help pregnant women receive financial assistance for institutional delivery. In Karnataka, eligible pregnant women can apply through their local health center.",
    "scheme_id": "123e4567-e89b-12d3-a456-426614174000",
    "sources": [
      "https://pmkisan.gov.in/"
    ],
    "disclaimer": "This AI assistant provides informational guidance based on stored government scheme records. It does not determine official eligibility or process government applications. Please verify details with official government portals."
  }
  ```
- **Important Error Responses**:
  - `404 Not Found`: Scheme UUID does not exist (`SCHEME_NOT_FOUND`).
  - `422 Unprocessable`: Invalid UUID format or message length > 2000 (`VALIDATION_ERROR`).
  - `503 Service Unavailable`: Gemini API unavailable or key unconfigured (`AI_SERVICE_UNAVAILABLE`).
  ```json
  {
    "success": false,
    "error": {
      "code": "AI_SERVICE_UNAVAILABLE",
      "message": "AI assistant is temporarily unavailable."
    }
  }
  ```

