const fs = require('fs');
const path = require('path');

const outDir = path.join(process.cwd(), 'src', 'frontend-build-artifact');
const outFile = path.join(outDir, 'build.txt');
const content = 'CalculadoraWebForms frontend placeholder build artifact\n';

fs.mkdirSync(outDir, { recursive: true });
if (!fs.existsSync(outFile) || fs.readFileSync(outFile, 'utf8') !== content) {
  fs.writeFileSync(outFile, content, 'utf8');
}
console.log('frontend build complete');
