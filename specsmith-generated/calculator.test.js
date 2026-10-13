import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

function runPython(code) {
  const result = spawnSync('python3', ['-c', code], { encoding: 'utf-8' });
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || 'python execution failed').trim());
  }
  return result.stdout.trim();
}

test('parse_number rejects None input', () => {
  const outcome = runPython(`
from calculator_app import parse_number
try:
    parse_number(None)
except Exception as exc:
    print(type(exc).__name__ + ':' + str(exc))
`);
  assert.match(outcome, /^TypeError:None is not a valid number$/);
});

test('parse_number rejects invalid numeric text', () => {
  const outcome = runPython(`
from calculator_app import parse_number
try:
    parse_number('not-a-number')
except Exception as exc:
    print(type(exc).__name__ + ':' + str(exc))
`);
  assert.match(outcome, /^ValueError:Invalid numeric input: not-a-number$/);
});

test('unknown operation is rejected', () => {
  const outcome = runPython(`
from calculator_app import calculate
try:
    calculate('unsupported', '1', '2')
except Exception as exc:
    print(type(exc).__name__ + ':' + str(exc))
`);
  assert.match(outcome, /^ValueError:Unknown operation: unsupported$/);
});

test('binary operations require a second operand', async (t) => {
  for (const operation of ['somar', 'subtrair', 'multiplicar', 'dividir', 'potencia']) {
    await t.test(operation, () => {
      const outcome = runPython(`
from calculator_app import calculate
try:
    calculate('${operation}', '1', None)
except Exception as exc:
    print(type(exc).__name__ + ':' + str(exc))
`);
      assert.match(outcome, /^TypeError:None is not a valid number$/);
    });
  }
});
