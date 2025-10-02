import pytest
import mongomock
from fastapi.testclient import TestClient
import main
import datetime

client = TestClient(main.app)

# mock DB
mongo_client = mongomock.MongoClient()
database = mongo_client.practica1
mock_collection = database.historial

def setup_module(module):
    
    mock_collection.delete_many({})

@pytest.mark.parametrize("a,b,expected", [
    ("1e3", "2e3", 3000.0),   
    ("0.0001", "0.0002", 0.0003)
])
def test_sum_scientific_and_small_floats(monkeypatch, a, b, expected):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    mock_collection.delete_many({})
    response = client.get(f"/calculadora/sum?a={a}&b={b}")
    assert response.status_code == 200
    payload = response.json()
    assert pytest.approx(payload["resultado"], rel=1e-9) == expected
    saved = mock_collection.find_one({"a": float(a), "b": float(b)})
    assert saved is not None
    assert pytest.approx(saved["resultado"], rel=1e-9) == expected
    assert saved.get("operacion") == "suma"
    assert "date" in saved and isinstance(saved["date"], datetime.datetime)

def test_non_numeric_parameters_return_422(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    response = client.get("/calculadora/sum?a=abc&b=1")
    assert response.status_code == 422

def test_multiple_sums_create_multiple_history_entries(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    mock_collection.delete_many({})
    # perform several sums
    client.get("/calculadora/sum?a=1&b=2")
    client.get("/calculadora/sum?a=10&b=20")
    client.get("/calculadora/sum?a=3.5&b=4.5")
    # fetch historial
    resp = client.get("/calculadora/historial")
    assert resp.status_code == 200
    historial = resp.json().get("historial", [])
    assert len(historial) == 3
    results = { (h["a"], h["b"]) : h["resultado"] for h in historial }
    assert (1.0, 2.0) in results and results[(1.0,2.0)] == 3.0
    assert (10.0, 20.0) in results and results[(10.0,20.0)] == 30.0
    assert (3.5, 4.5) in results and results[(3.5,4.5)] == 8.0

import pytest
import mongomock
from fastapi.testclient import TestClient
import main
import datetime

client = TestClient(main.app)

# mock DB
mongo_client = mongomock.MongoClient()
database = mongo_client.practica1
mock_collection = database.historial

def setup_module(module):
    # ensure clean collection before module tests
    mock_collection.delete_many({})

@pytest.mark.parametrize("a,b,expected", [
    ("1e3", "2e3", 3000.0),   # scientific notation
    ("0.0001", "0.0002", 0.0003)
])
def test_sum_scientific_and_small_floats(monkeypatch, a, b, expected):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    mock_collection.delete_many({})
    response = client.get(f"/calculadora/sum?a={a}&b={b}")
    assert response.status_code == 200
    payload = response.json()
    assert pytest.approx(payload["resultado"], rel=1e-9) == expected
    saved = mock_collection.find_one({"a": float(a), "b": float(b)})
    assert saved is not None
    assert pytest.approx(saved["resultado"], rel=1e-9) == expected
    assert saved.get("operacion") == "suma"
    assert "date" in saved and isinstance(saved["date"], datetime.datetime)

def test_non_numeric_parameters_return_422(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    response = client.get("/calculadora/sum?a=abc&b=1")
    assert response.status_code == 422

def test_multiple_sums_create_multiple_history_entries(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    mock_collection.delete_many({})
    # perform several sums
    client.get("/calculadora/sum?a=1&b=2")
    client.get("/calculadora/sum?a=10&b=20")
    client.get("/calculadora/sum?a=3.5&b=4.5")
    # fetch historial
    resp = client.get("/calculadora/historial")
    assert resp.status_code == 200
    historial = resp.json().get("historial", [])
    assert len(historial) == 3
    results = { (h["a"], h["b"]) : h["resultado"] for h in historial }
    assert (1.0, 2.0) in results and results[(1.0,2.0)] == 3.0
    assert (10.0, 20.0) in results and results[(10.0,20.0)] == 30.0
    assert (3.5, 4.5) in results and results[(3.5,4.5)] == 8.0