import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [op, setOp] = useState("sum");
  const [result, setResult] = useState(null);
  const [historial, setHistorial] = useState([]);

  // new state for filtering/sorting
  const [filterOp, setFilterOp] = useState("all"); // all | sum | sub | mul | div
  const [sortBy, setSortBy] = useState("date"); // date | resultado
  const [order, setOrder] = useState("desc"); // asc | desc

  useEffect(() => {
    fetchHist();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterOp, sortBy, order]);

  const fetchHist = async () => {
    try {
      const params = new URLSearchParams();
      if (filterOp && filterOp !== "all") params.append("op", filterOp);
      if (sortBy) params.append("sort_by", sortBy);
      if (order) params.append("order", order);

      const url = `http://localhost:8000/calculadora/historial?${params.toString()}`;
      const r = await fetch(url);
      const j = await r.json();
      setHistorial(j.historial || []);
    } catch (e) {
      console.error(e);
      setHistorial([]);
    }
  };

  const handleCalc = async () => {
    if (a === "" || b === "") {
      alert("Ingrese ambos números");
      return;
    }
    const endpointMap = {
      sum: "sum",
      sub: "sub",
      mul: "mul",
      div: "div",
    };
    const endpoint = endpointMap[op];
    const url = `http://localhost:8000/calculadora/${endpoint}?a=${encodeURIComponent(
      a
    )}&b=${encodeURIComponent(b)}`;
    try {
      const r = await fetch(url);
      if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: "Error" }));
        alert("Error: " + (err.detail || r.status));
        return;
      }
      const j = await r.json();
      setResult(j.resultado);
      fetchHist(); // refresh with current filters/sort
    } catch (e) {
      alert("Error de conexión");
    }
  };

  return (
    <div className="App">
      <div className="card">
        <header className="card-header">
          <h1>Calculadora cabrona de numeros</h1>
        </header>

        <div className="card-body">
          <div className="form">
            <input
              type="number"
              step="any"
              placeholder="a"
              value={a}
              onChange={(e) => setA(e.target.value)}
              className="input"
            />
            <input
              type="number"
              step="any"
              placeholder="b"
              value={b}
              onChange={(e) => setB(e.target.value)}
              className="input"
            />
            <select
              value={op}
              onChange={(e) => setOp(e.target.value)}
              className="select"
            >
              <option value="sum">Sumar</option>
              <option value="sub">Restar</option>
              <option value="mul">Multiplicar</option>
              <option value="div">Dividir</option>
            </select>
            <button onClick={handleCalc} className="btn-primary">
              Calcular
            </button>
          </div>

          <div className="result card-result">
            <h2>Resultado</h2>
            <div className="result-value">
              {result !== null ? result : "-"}
            </div>
          </div>

          <div className="historial-controls" style={{ marginTop: 12 }}>
            <label>
              Filtrar:
              <select
                value={filterOp}
                onChange={(e) => setFilterOp(e.target.value)}
                className="select small"
              >
                <option value="all">Todas</option>
                <option value="sum">Suma</option>
                <option value="sub">Resta</option>
                <option value="mul">Multiplicacion</option>
                <option value="div">Division</option>
              </select>
            </label>

            <label>
              Ordenar por:
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="select small"
              >
                <option value="date">Fecha</option>
                <option value="resultado">Resultado</option>
              </select>
            </label>

            <label>
              Dirección:
              <select
                value={order}
                onChange={(e) => setOrder(e.target.value)}
                className="select small"
              >
                <option value="desc">Desc</option>
                <option value="asc">Asc</option>
              </select>
            </label>
          </div>

          <div className="historial" style={{ marginTop: 16 }}>
            <h2>Historial de operaciones</h2>
            <ul className="hist-list">
              {historial.map((h, idx) => (
                <li key={idx} className="hist-item">
                  <div className="hist-meta">
                    <span
                      className={`op-badge ${h.operacion || ""}`}
                    >
                      {h.operacion || "?"}
                    </span>
                    <span className="hist-date">
                      {h.date ? new Date(h.date).toLocaleString() : "-"}
                    </span>
                  </div>
                  <div className="hist-content">
                    <div className="hist-inputs">
                      {h.nums ? h.nums.join(", ") : `${h.a} , ${h.b}`}
                    </div>
                    <div className="hist-result">= {h.resultado}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <footer className="card-footer">RIQIPERES</footer>
      </div>
    </div>
  );
}

export default App;

