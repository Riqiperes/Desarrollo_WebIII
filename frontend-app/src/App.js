import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [op, setOp] = useState("sum");
  const [result, setResult] = useState(null);
  const [historial, setHistorial] = useState([]);

  useEffect(() => {
    fetchHist();
  }, []);

  const fetchHist = async () => {
    try {
      const r = await fetch("http://localhost:8000/calculadora/historial");
      const j = await r.json();
      setHistorial(j.historial || []);
    } catch (e) {
      console.error(e);
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
      fetchHist();
    } catch (e) {
      alert("Error de conexión");
    }
  };

  return (
    <div className="App">
      <h1>Calculadora</h1>
      <div className="form">
        <input
          type="number"
          step="any"
          placeholder="a"
          value={a}
          onChange={(e) => setA(e.target.value)}
        />
        <input
          type="number"
          step="any"
          placeholder="b"
          value={b}
          onChange={(e) => setB(e.target.value)}
        />
        <select value={op} onChange={(e) => setOp(e.target.value)}>
          <option value="sum">Sumar</option>
          <option value="sub">Restar</option>
          <option value="mul">Multiplicar</option>
          <option value="div">Dividir</option>
        </select>
        <button onClick={handleCalc}>Calcular</button>
      </div>

      <div className="result">
        <h2>Resultado</h2>
        <div>{result !== null ? result : "-"}</div>
      </div>

      <div className="historial">
        <h2>Historial de operaciones</h2>
        <ul>
          {historial.map((h, idx) => (
            <li key={idx}>
              [{new Date(h.date).toLocaleString()}] {h.operacion}: {h.a} , {h.b} =&gt;{" "}
              {h.resultado}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;

