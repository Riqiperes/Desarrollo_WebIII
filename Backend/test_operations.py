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

def setup_function():
    mock_collection.delete_many({})

def test_sum_and_save(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/sum?a=3&b=2")
    assert resp.status_code == 200
    assert resp.json() == {"a": 3.0, "b": 2.0, "resultado": 5.0}
    saved = mock_collection.find_one({"a": 3.0, "b": 2.0})
    assert saved and saved["operacion"] == "suma"

def test_subtract_ok(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/sub?a=5&b=2")
    assert resp.status_code == 200
    assert resp.json()["resultado"] == 3.0
    saved = mock_collection.find_one({"operacion": "resta"})
    assert saved

def test_subtract_negative_result_forbidden(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/sub?a=1&b=2")
    assert resp.status_code == 400

def test_multiply(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/mul?a=4&b=2.5")
    assert resp.status_code == 200
    assert resp.json()["resultado"] == 10.0
    saved = mock_collection.find_one({"operacion": "multiplicacion"})
    assert saved

def test_divide(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/div?a=10&b=2")
    assert resp.status_code == 200
    assert resp.json()["resultado"] == 5.0
    saved = mock_collection.find_one({"operacion": "division"})
    assert saved

def test_divide_by_zero(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/div?a=1&b=0")
    assert resp.status_code == 400

def test_negative_input_not_allowed(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    resp = client.get("/calculadora/sum?a=-1&b=2")
    assert resp.status_code == 400

def test_historial_returns_all(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    mock_collection.delete_many({})
    # insert three ops
    client.get("/calculadora/sum?a=1&b=1")
    client.get("/calculadora/mul?a=2&b=3")
    client.get("/calculadora/div?a=10&b=2")
    res = client.get("/calculadora/historial")
    assert res.status_code == 200
    h = res.json()["historial"]
    assert len(h) == 3
    ops = {entry["operacion"] for entry in h}
    assert {"suma", "multiplicacion", "division"} <= ops