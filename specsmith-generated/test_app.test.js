const test = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');

const projectRoot = __dirname;

function runCalculator(operation, nro1, nro2) {
  const script = `
from app import calculate
print(calculate(${JSON.stringify(operation)}, ${JSON.stringify(nro1)}, ${JSON.stringify(nro2)}))
`;
  const result = spawnSync('python3', ['-c', script], {
    cwd: projectRoot,
    encoding: 'utf8'
  });

  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || 'python execution failed');
  }

  return result.stdout.trim();
}

function renderPage() {
  const script = `
from app import render_page
print(render_page())
`;
  const result = spawnSync('python3', ['-c', script], {
    cwd: projectRoot,
    encoding: 'utf8'
  });

  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || 'python execution failed');
  }

  return result.stdout;
}

test('renders calculator controls on the main page', () => {
  const html = renderPage();
  assert.match(html, /CalculadoraWebForms/);
  assert.match(html, /name="txtNro1"/);
  assert.match(html, /name="txtNro2"/);
  assert.match(html, /value="somar"/);
  assert.match(html, /value="subtrair"/);
  assert.match(html, /value="multiplicar"/);
  assert.match(html, /value="dividir"/);
  assert.match(html, /value="potencia"/);
  assert.match(html, /value="raizq"/);
  assert.match(html, /id="lbResultado"/);
});

test('performs arithmetic operations through calculator logic', () => {
  assert.equal(runCalculator('somar', '2', '3'), '5.0');
  assert.equal(runCalculator('subtrair', '7', '2'), '5.0');
  assert.equal(runCalculator('multiplicar', '4', '2.5'), '10.0');
  assert.equal(runCalculator('dividir', '9', '3'), '3.0');
  assert.equal(runCalculator('potencia', '2', '3'), '8.0');
  assert.equal(runCalculator('raizq', '9', '0'), '3.0');
});

test('preserves source-like invalid input failure behavior', () => {
  const script = `
from app import calculate
calculate('somar', 'abc', '1')
`;
  const result = spawnSync('python3', ['-c', script], {
    cwd: projectRoot,
    encoding: 'utf8'
  });

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /ValueError/);
});
