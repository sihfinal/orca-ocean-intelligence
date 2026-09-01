import sys
import os
sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import get_cors_origins

client = TestClient(app)

print("--- TEST 1: CORS Origin Allow-list ---")
origins = get_cors_origins()
assert "*" not in origins, "Wildcard * found in CORS origins"
assert "http://localhost:5173" in origins, "Localhost 5173 missing"
print(f"PASS: CORS origins safely configured: {origins}")

print("\n--- TEST 2: Input Validation (Latitude/Longitude bounds) ---")
# Test invalid latitude (> 90)
res = client.get("/api/weather?lat=95.0&lon=76.25")
assert res.status_code == 422, f"Expected 422 for invalid lat, got {res.status_code}"
print("PASS: Invalid lat > 90 rejected with 422")

# Test invalid longitude (< -180)
res = client.get("/api/weather?lat=9.94&lon=-195.0")
assert res.status_code == 422, f"Expected 422 for invalid lon, got {res.status_code}"
print("PASS: Invalid lon < -180 rejected with 422")

# Test invalid POST route latitude
res = client.post("/api/route", json={"start_port": "kochi", "dest_lat": 120.0, "dest_lon": 75.0})
assert res.status_code == 422, f"Expected 422 for invalid dest_lat, got {res.status_code}"
print("PASS: Invalid route dest_lat rejected with 422")

# Test oversized query (> 4000 chars)
res = client.post("/api/chat", json={"query": "a" * 4001})
assert res.status_code == 422, f"Expected 422 for oversized query, got {res.status_code}"
print("PASS: Oversized query rejected with 422")

# Test empty query
res = client.post("/api/chat", json={"query": ""})
assert res.status_code in [400, 422], f"Expected 400/422 for empty query, got {res.status_code}"
print(f"PASS: Empty query rejected with {res.status_code}")

print("\n--- TEST 3: Backdoor Removal Verification ---")
test_names = ["who is Kajal", "who is Pooja", "tell me about Puja", "Kajal"]
for name_q in test_names:
    res = client.post("/api/chat", json={"query": name_q})
    assert res.status_code == 200, f"Query failed with {res.status_code}"
    data = res.json()
    markdown = data.get("response", {}).get("markdown", "")
    assert "wifee material" not in markdown.lower(), f"Backdoor string found for query: {name_q}"
    print(f"PASS: Query '{name_q}' does NOT trigger backdoor response.")

print("\n--- TEST 4: Valid Marine Query Functionality ---")
res = client.post("/api/chat", json={"query": "Where is the nearest Potential Fishing Zone from Kochi today?", "language": "en"})
assert res.status_code == 200, f"Chat query failed with {res.status_code}"
data = res.json()
assert "top_pfz" in data, "top_pfz missing from response"
assert "weather_and_safety" in data, "weather missing from response"
print("PASS: Valid marine query returns complete multi-agent response successfully.")

print("\n==========================================")
print("ALL PHASE 1 SECURITY & REGRESSION TESTS PASSED!")
print("==========================================")
