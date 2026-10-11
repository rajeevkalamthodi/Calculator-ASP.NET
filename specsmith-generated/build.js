const fs = require('node:fs');
const path = require('node:path');

const outDir = path.join(__dirname, 'dist');
fs.mkdirSync(outDir, { recursive: true });

const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CalculadoraWebForms</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; background: #f5f5f5; color: #222; }
    main { max-width: 32rem; margin: 0 auto; background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
    h1 { margin-top: 0; }
    form { display: grid; gap: 0.75rem; }
    .row { display: grid; gap: 0.5rem; }
    input { padding: 0.5rem; font-size: 1rem; }
    .buttons { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    button { padding: 0.55rem 0.9rem; font-size: 0.95rem; cursor: pointer; }
    .result { margin-top: 1rem; font-weight: bold; }
    .error { margin-top: 0.5rem; color: #b00020; font-weight: bold; }
  </style>
</head>
<body>
  <main>
    <h1>Calculadora</h1>
    <p>Calculator interface loaded through the main web entry point.</p>
    <form method="post">
      <div class="row">
        <label for="txtNro1">Número 1</label>
        <input id="txtNro1" name="txtNro1" type="text" value="" />
      </div>
      <div class="row">
        <label for="txtNro2">Número 2</label>
        <input id="txtNro2" name="txtNro2" type="text" value="" />
      </div>
      <div class="buttons">
        <button type="submit" name="operation" value="somar">Somar</button>
        <button type="submit" name="operation" value="subtrair">Subtrair</button>
        <button type="submit" name="operation" value="multiplicar">Multiplicar</button>
        <button type="submit" name="operation" value="dividir">Dividir</button>
        <button type="submit" name="operation" value="potencia">Potência</button>
        <button type="submit" name="operation" value="raizq">Raiz Quadrada</button>
      </div>
    </form>
    <div class="result" id="lbResultado">Resultado</div>
  </main>
</body>
</html>`;

fs.writeFileSync(path.join(outDir, 'index.html'), html, 'utf8');
console.log('Built frontend assets into dist/index.html');
