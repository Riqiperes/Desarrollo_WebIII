import pytest
import mongomock
from fastapi.testclient import TestClient
import main
import datetime
import json

client = TestClient(main.app)

# mock DB
mongo_client = mongomock.MongoClient()
database = mongo_client.practica1
mock_collection = database.historial

def setup_function():
    mock_collection.delete_many({})

def test_historial_filter_and_sort(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    now = datetime.datetime(2025, 10, 1, 10, 0, tzinfo=datetime.timezone.utc)
    mock_collection.insert_one({"a": 1.0, "b": 1.0, "resultado": 2.0, "operacion": "suma", "date": now})
    mock_collection.insert_one({"a": 2.0, "b": 2.0, "resultado": 4.0, "operacion": "suma", "date": now + datetime.timedelta(minutes=5)})
    mock_collection.insert_one({"a": 5.0, "b": 2.0, "resultado": 3.0, "operacion": "resta", "date": now + datetime.timedelta(minutes=10)})

    # filter suma and sort by resultado asc
    res = client.get("/calculadora/historial?op=sum&sort_by=resultado&order=asc")
    assert res.status_code == 200
    hist = res.json()["historial"]
    assert all(entry["operacion"] == "suma" for entry in hist)
    resultados = [h["resultado"] for h in hist]
    assert resultados == sorted(resultados)

def test_personalized_error_on_negative(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    res = client.get("/calculadora/sum?a=-1&b=2")
    assert res.status_code == 400
    body = res.json()
    assert "detail" in body
    assert body["detail"]["op"] == "suma"
    assert body["detail"]["nums"] == [-1.0, 2.0]

def test_batch_success_and_saves(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    mock_collection.delete_many({})
    payload = [
        {"op": "sum", "nums": [2, 4]},
        {"op": "mul", "nums": [2, 4]}
    ]
    res = client.post("/calculadora/batch", json=payload)
    assert res.status_code == 200
    assert res.json() == [{"op": "suma", "result": 6}, {"op": "multiplicacion", "result": 8}]
    # saved
    saved = list(mock_collection.find({}))
    assert len(saved) == 2
    assert saved[0]["nums"] == [2, 4]

def test_batch_divide_by_zero(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    payload = [{"op": "div", "nums": [4, 0]}]
    res = client.post("/calculadora/batch", json=payload)
    assert res.status_code == 400
    body = res.json()
    assert "detail" in body
    assert body["detail"]["op"] == "division"
    assert body["detail"]["nums"] == [4.0, 0.0]