const fs = require('node:fs');
const path = require('node:path');

const outDir = path.join(__dirname, 'dist');
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(
  path.join(outDir, 'index.html'),
  '<!DOCTYPE html><html><head><meta charset="utf-8"><title>CalculadoraWebForms</title></head><body><p>build ok</p></body></html>\n',
  'utf8'
);
process.stdout.write('build ok\n');
