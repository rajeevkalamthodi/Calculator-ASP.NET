import React, { useState } from 'react';

// Operations mirror the ASP.NET Web Forms buttons (index.aspx.cs).
const OPERATIONS = [
  { id: 'somar', label: 'Somar', unary: false },
  { id: 'subtrair', label: 'Subtrair', unary: false },
  { id: 'multiplicar', label: 'Multiplicar', unary: false },
  { id: 'dividir', label: 'Dividir', unary: false },
  { id: 'potencia', label: 'Potencia', unary: false },
  { id: 'raizq', label: 'Raiz Quadrada', unary: true },
];

export default function App() {
  const [nro1, setNro1] = useState('');
  const [nro2, setNro2] = useState('');
  const [resultado, setResultado] = useState('');
  const [error, setError] = useState('');

  async function handleOperation(op) {
    setError('');
    try {
      const resp = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ operation: op.id, nro1, nro2 }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        setResultado('');
        setError(data.error || 'Erro ao calcular.');
        return;
      }
      setResultado(data.result);
    } catch (e) {
      setResultado('');
      setError('Erro de conexao.');
    }
  }

  return (
    <div className="calculadora">
      <h1>CalculadoraWebForms</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <div className="field">
          <label htmlFor="txtNro1">Numero 1</label>
          <input
            id="txtNro1"
            type="text"
            value={nro1}
            onChange={(e) => setNro1(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="txtNro2">Numero 2</label>
          <input
            id="txtNro2"
            type="text"
            value={nro2}
            onChange={(e) => setNro2(e.target.value)}
          />
        </div>
        <div className="buttons">
          {OPERATIONS.map((op) => (
            <button
              key={op.id}
              type="button"
              onClick={() => handleOperation(op)}
            >
              {op.label}
            </button>
          ))}
        </div>
      </form>
      <div className="resultado">
        <label htmlFor="lbResultado">Resultado</label>
        <span id="lbResultado" data-testid="lbResultado">
          {resultado}
        </span>
      </div>
      {error && (
        <div className="error" role="alert" data-testid="error">
          {error}
        </div>
      )}
    </div>
  );
}
