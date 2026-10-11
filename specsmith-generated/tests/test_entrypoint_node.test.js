const test = require('node:test');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');

async function waitForReady(port) {
  const deadline = Date.now() + 10000;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/health`);
      if (response.status === 200) {
        return;
      }
    } catch (error) {
      lastError = error;
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  throw new Error(`Server did not become ready: ${lastError}`);
}

test('application loads through the web entry point and exposes health', async (t) => {
  const port = 8124;
  const server = spawn('python3', ['main.py'], {
    env: { ...process.env, PORT: String(port) },
    stdio: 'ignore',
  });

  t.after(() => {
    if (!server.killed) {
      server.kill('SIGTERM');
    }
  });

  await waitForReady(port);

  const healthResponse = await fetch(`http://127.0.0.1:${port}/health`);
  assert.equal(healthResponse.status, 200);
  assert.equal(await healthResponse.text(), 'ok');

  const rootResponse = await fetch(`http://127.0.0.1:${port}/`);
  assert.equal(rootResponse.status, 200);
  const html = await rootResponse.text();
  assert.match(html, /<h1>Calculadora<\/h1>/);
  assert.match(html, /txtNro1/);
  assert.match(html, /txtNro2/);
  assert.match(html, /Somar/);
  assert.match(html, /Resultado/);
});
