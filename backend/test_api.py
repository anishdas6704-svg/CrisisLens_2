import json
import requests
import asyncio
import websockets

API_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/api/v1/ws/FLD-KOL-2026-0947"

def test_rest_endpoints():
    print("--- 1. Testing Health Endpoint ---")
    r = requests.get(f"{API_URL}/health")
    print(f"Status: {r.status_code}, Body: {r.json()}")
    assert r.status_code == 200

    print("\n--- 2. Testing Dashboard Endpoint ---")
    r = requests.get(f"{API_URL}/crises/dashboard")
    print(f"Status: {r.status_code}, Total Crises: {r.json().get('total_crises')}, Recent Updates: {len(r.json().get('recent_updates', []))}")
    assert r.status_code == 200

    print("\n--- 3. Testing List Crises Endpoint ---")
    r = requests.get(f"{API_URL}/crises/?limit=20")
    crises = r.json()
    print(f"Status: {r.status_code}, Found {len(crises)} crises")
    for c in crises[:3]:
        print(f"  - [{c['id']}] {c['name']} ({c['status']})")
    assert r.status_code == 200

    print("\n--- 4. Testing Crisis Updates Endpoint ---")
    r = requests.get(f"{API_URL}/crises/FLD-KOL-2026-0947/updates/?limit=8")
    updates = r.json()
    print(f"Status: {r.status_code}, Found {len(updates)} updates")
    for u in updates[:2]:
        print(f"  - {u['raw_text'][:50]}... [Type: {u.get('ai_extracted', {}).get('entity_type')}]")
    assert r.status_code == 200

    print("\n--- 5. Testing Process Update (AI Engine) ---")
    sample_payload = {
        "raw_text": "Highway 12 northbound is now completely closed due to severe flooding near Sector 4. Emergency NDRF crews dispatched with boats.",
        "source": "agency"
    }
    r = requests.post(f"{API_URL}/crises/FLD-KOL-2026-0947/updates/process", json=sample_payload)
    print(f"Status: {r.status_code}")
    res = r.json()
    print(f"Entity: {res.get('entity')}")
    print(f"Change Detected: {res.get('change_detected')}")
    print(f"AI Extracted: {res.get('ai_extracted')}")
    assert r.status_code == 200

async def test_websocket():
    print("\n--- 6. Testing WebSocket Connection ---")
    async with websockets.connect(WS_URL) as ws:
        await ws.send("ping")
        resp = await ws.recv()
        print(f"WebSocket received: {resp}")
        assert resp == "pong"
        print("WebSocket live test PASSED!")

if __name__ == "__main__":
    test_rest_endpoints()
    asyncio.run(test_websocket())
    print("\n✨ ALL TESTS PASSED! Backend is fully functional.")
