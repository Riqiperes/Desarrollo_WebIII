import pytest
import mongomock
from fastapi.testclient import TestClient
import main 
import datetime

client = TestClient(main.app)

#mock
mongo_client = mongomock.MongoClient()
database = mongo_client.practica1
mock_collection = database.historial


@pytest.mark.parametrize("a, b, expected", [
    (2, 2, 4),
    (0, 0, 0),
    (-1, 1, 0),
    (2.5, 2.5, 5.0),
    (1e10, 1e10, 2e10)
])
def test_sum_numbers(monkeypatch, a, b, expected):
    
    monkeypatch.setattr(main, "collection_historial", mock_collection)

   
    mock_collection.delete_many({})

    response = client.get(f"/calculadora/sum?a={a}&b={b}")
    
    
    assert response.status_code == 200
    assert response.json() == {"a": a, "b": b, "resultado": expected}
    
    
    saved = mock_collection.find_one({"a": a, "b": b})
    assert saved is not None
    assert saved["resultado"] == expected


def test_historial(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", mock_collection)
    
    
    doc_sum = {
        "a": 10000000000.0,
        "b": 10000000000.0,
        "resultado": 20000000000.0,
        "date": datetime.datetime(2025, 10, 1, 10, 24, 19, 116000, tzinfo=datetime.timezone.utc),
        "operacion": "suma"
    }
    mock_collection.insert_one(doc_sum)
    
    response = client.get("/calculadora/historial")
    assert response.status_code == 200
    
    expected_historial = []
    for doc in mock_collection.find({}):
        expected_historial.append({
            "a": doc["a"],
            "b": doc["b"],
            "resultado": doc["resultado"],
            "operacion": doc["operacion"],  
            "date": doc["date"].isoformat()
        })
    
    
    
    assert response.json() == {"historial": expected_historial}