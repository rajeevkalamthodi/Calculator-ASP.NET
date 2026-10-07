const test = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');

test('npm test executes the complete Python calculator and configuration suite', () => {
  const result = spawnSync(process.platform === 'win32' ? 'python' : 'python3',
    ['-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], {
      cwd: path.resolve(__dirname, '..'), encoding: 'utf8', timeout: 60000, maxBuffer: 2 * 1024 * 1024
    });
  assert.ifError(result.error);
  const output = result.stdout + result.stderr;
  assert.equal(result.signal, null, output);
  assert.equal(result.status, 0, output);
  const count = /^Ran (\d+) tests? in /m.exec(output);
  assert.ok(count && Number(count[1]) >= 18, `Expected all 11 calculator and 7 configuration cases:\n${output}`);
  assert.match(output, /^OK\s*$/m);
});
