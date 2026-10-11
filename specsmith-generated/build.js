const fs = require('node:fs');
const path = require('node:path');

const outDir = path.join(__dirname, 'dist');
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(
  path.join(outDir, '.build-marker'),
  'calculadorawebforms build complete\n',
  'utf8'
);
console.log('Built frontend assets into dist/');
