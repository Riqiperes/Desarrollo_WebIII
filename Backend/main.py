from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Any, Dict
import datetime
import operator
import functools

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


def _normalize_op(op: str) -> str:
    op = (op or "").lower()
    mapping = {
        "sum": "suma",
        "suma": "suma",
        "add": "suma",
        "sub": "resta",
        "resta": "resta",
        "subtract": "resta",
        "mul": "multiplicacion",
        "multiplicacion": "multiplicacion",
        "multiply": "multiplicacion",
        "div": "division",
        "division": "division",
        "divide": "division",
    }
    return mapping.get(op, op)


def _raise_op_error(op: str, nums: Any, detail: str, status: int = 400):
    payload = {"op": _normalize_op(op) if isinstance(op, str) else op, "nums": nums, "detail": detail}
    raise HTTPException(status_code=status, detail=payload)


def _validate_non_negative_iter(nums: List[float], op_name: str):
    for n in nums:
        if n < 0:
            _raise_op_error(op_name, nums, "Los números no pueden ser negativos", 400)


class BatchItem(BaseModel):
    op: str
    nums: List[float]


@app.get("/calculadora/sum")
def sumar(a: float, b: float):
    op_name = "suma"
    _validate_non_negative_iter([a, b], op_name)
    resultado = a + b
    document = {"a": a, "b": b, "resultado": resultado, "operacion": op_name, "date": datetime.datetime.now(tz=datetime.timezone.utc)}
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/sub")
def restar(a: float, b: float):
    op_name = "resta"
    _validate_non_negative_iter([a, b], op_name)
    resultado = a - b
    if resultado < 0:
        _raise_op_error(op_name, [a, b], "Resultado no puede ser negativo", 400)
    document = {"a": a, "b": b, "resultado": resultado, "operacion": op_name, "date": datetime.datetime.now(tz=datetime.timezone.utc)}
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/mul")
def multiplicar(a: float, b: float):
    op_name = "multiplicacion"
    _validate_non_negative_iter([a, b], op_name)
    resultado = a * b
    document = {"a": a, "b": b, "resultado": resultado, "operacion": op_name, "date": datetime.datetime.now(tz=datetime.timezone.utc)}
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/div")
def dividir(a: float, b: float):
    op_name = "division"
    _validate_non_negative_iter([a, b], op_name)
    if b == 0:
        _raise_op_error(op_name, [a, b], "No se puede dividir por cero", 400)
    resultado = a / b
    document = {"a": a, "b": b, "resultado": resultado, "operacion": op_name, "date": datetime.datetime.now(tz=datetime.timezone.utc)}
    collection_historial.insert_one(document)
    return {"a": a, "b": b, "resultado": resultado}


@app.get("/calculadora/historial")
def obtener_historial(
    op: Optional[str] = None,
    sort_by: Optional[str] = "date",  # "date" or "resultado"
    order: Optional[str] = "desc",  # "asc" or "desc"
):
    # build query (normalize op names)
    query = {}
    if op:
        query["operacion"] = _normalize_op(op)

    # fetch matching documents
    docs = list(collection_historial.find(query))

    # prepare date objects for sorting
    for d in docs:
        d["_date_obj"] = d.get("date") if isinstance(d.get("date"), datetime.datetime) else None

    # validate sort_by
    if sort_by not in ("date", "resultado"):
        raise HTTPException(status_code=400, detail={"detail": "sort_by must be 'date' or 'resultado'"})

    # determine order
    reverse = True if (order or "").lower() == "desc" else False

    # sort documents
    if sort_by == "date":
        min_date = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        docs.sort(key=lambda x: x["_date_obj"] or min_date, reverse=reverse)
    else:  # sort_by == "resultado"
        docs.sort(key=lambda x: x.get("resultado", 0), reverse=reverse)

    # build standardized response
    historial = []
    for operacion in docs:
        entry: Dict[str, Any] = {
            "operacion": operacion.get("operacion", ""),
            "resultado": operacion.get("resultado"),
            "date": operacion.get("date").isoformat() if operacion.get("date") else None
        }
        if "nums" in operacion:
            entry["nums"] = operacion["nums"]
        else:
            entry["a"] = operacion.get("a")
            entry["b"] = operacion.get("b")
        historial.append(entry)

    return {"historial": historial}


@app.post("/calculadora/batch")
def batch_operations(items: List[BatchItem]):
    results = []
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    for it in items:
        op_raw = it.op
        op = _normalize_op(op_raw)
        nums = it.nums
        if not nums or len(nums) < 1:
            _raise_op_error(op, nums, "La lista de números no puede estar vacía", 400)
        _validate_non_negative_iter(nums, op)
        # compute
        if op == "suma":
            resultado = sum(nums)
        elif op == "multiplicacion":
            resultado = functools.reduce(operator.mul, nums, 1.0)
        elif op == "resta":
            resultado = nums[0] - sum(nums[1:]) if len(nums) > 1 else nums[0]
            if resultado < 0:
                _raise_op_error(op, nums, "Resultado no puede ser negativo", 400)
        elif op == "division":
            # ensure no divisor is zero
            for d in nums[1:]:
                if d == 0:
                    _raise_op_error(op, nums, "No se puede dividir por cero", 400)
            resultado = nums[0]
            for d in nums[1:]:
                resultado = resultado / d
        else:
            _raise_op_error(op, nums, f"Operación no soportada: {op_raw}", 400)

        # save document with nums
        document = {"nums": nums, "resultado": resultado, "operacion": op, "date": now}
        collection_historial.insert_one(document)
        results.append({"op": op, "result": resultado})

    return results

