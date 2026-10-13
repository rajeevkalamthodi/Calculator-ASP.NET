const fs = require('fs');
const path = require('path');

const outDir = path.join(process.cwd(), 'src', 'frontend-build-artifact');
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(
  path.join(outDir, 'build.txt'),
  'CalculadoraWebForms frontend placeholder build artifact\n',
  'utf8'
);
console.log('frontend build complete');
