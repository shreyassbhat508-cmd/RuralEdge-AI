import json
import os
import sys

# Ensure env vars and python paths are configured
if "SUPABASE_URL" not in os.environ:
    os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
if "SUPABASE_KEY" not in os.environ:
    os.environ["SUPABASE_KEY"] = "mock-key-12345"

sys.path.insert(0, "c:\\Users\\supra\\OneDrive\\Desktop\\RuralEdge\\RuralEdge-AI")
sys.path.insert(0, "c:\\Users\\supra\\OneDrive\\Desktop\\RuralEdge\\RuralEdge-AI\\backend")

from fastapi.testclient import TestClient
from app.main import app

def run_demo_verification():
    client = TestClient(app)
    
    payload = {
        "location": {
            "state": "Karnataka",
            "district": "Kodagu",
            "village": "Madikeri"
        },
        "business_category": "Dairy",
        "margin_capital": 100000,
        "project_cost": 1000000
    }
    
    print("--- Sending POST /api/business/analyze request ---")
    response = client.post("/api/business/analyze", json=payload)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=2))
    
    # Assertions for internal consistency
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # 1. Location
    assert data["business"]["category"] == "Dairy"
    assert data["business"]["location"]["state"] == "Karnataka"
    assert data["business"]["location"]["district"] == "Kodagu"
    assert data["business"]["location"]["village"] == "Madikeri"
    
    # 2. Finance
    finance = data["finance"]
    assert finance["project_cost"] == 1000000.0
    assert finance["own_contribution"] == 100000.0
    assert finance["loan_amount"] == 900000.0  # 10,00,000 - 1,00,000
    assert finance["emi"] > 0
    assert finance["total_interest"] > 0
    assert finance["payback_months"] == 60
    
    # 3. Market
    market = data["market"]
    assert "source" in market
    assert "status" in market
    
    # 4. Opportunity
    opp = data["opportunity"]
    assert 0 <= opp["score"] <= 100
    assert opp["level"] in ["Low", "Medium", "High"]
    assert "components" in opp
    for k in ["market", "competition", "financial", "location", "affordability"]:
        assert k in opp["components"]
        assert 0 <= opp["components"][k] <= 100
        
    # 5. Scheme
    scheme = data["scheme"]
    assert "status" in scheme
    
    # 6. SWOT
    swot = data["swot"]
    assert len(swot["strengths"]) > 0
    
    print("\n✅ All assertions passed successfully for the demo scenario!")

if __name__ == "__main__":
    run_demo_verification()
