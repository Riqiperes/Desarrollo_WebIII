from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
mongo_client = MongoClient("mongodb://admin_user:web3@mongo:27017/")
database = mongo_client["practica1"]
collection_historial = database["historial"]


def _validate_non_negative(a: float, b: float):
    if a < 0 or b < 0:
        raise HTTPException(status_code=400, detail="Los números no pueden ser negativos")


@app.get("/calculadora/sum")
def sumar(a: float, b: float):
    _validate_non_negative(a, b)
    resultado = a + b
    document = {
        "a": a,
        "b": b,
        "resultado": resultado,
        "operacion": "suma",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/sub")
def restar(a: float, b: float):
    _validate_non_negative(a, b)
    resultado = a - b
    document = {
        "a": a,
        "b": b,
        "resultado": resultado,
        "operacion": "resta",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/mul")
def multiplicar(a: float, b: float):
    _validate_non_negative(a, b)
    resultado = a * b
    document = {
        "a": a,
        "b": b,
        "resultado": resultado,
        "operacion": "multiplicacion",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/div")
def dividir(a: float, b: float):
    _validate_non_negative(a, b)
    if b == 0:
        raise HTTPException(status_code=400, detail="No se puede dividir por cero")
    resultado = a / b
    document = {
        "a": a,
        "b": b,
        "resultado": resultado,
        "operacion": "division",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/historial")
def obtener_historial():
    operaciones = collection_historial.find({})
    historial = []
    for operacion in operaciones:
        historial.append({
            "a": operacion["a"],
            "b": operacion["b"],
            "resultado": operacion["resultado"],
            "operacion": operacion.get("operacion", ""),
            "date": operacion["date"].isoformat() if "date" in operacion else None
        })
    return {"historial": historial}

