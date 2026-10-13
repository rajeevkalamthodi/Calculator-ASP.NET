const fs = require('fs');
const path = require('path');

const distDir = path.join(process.cwd(), 'src', 'dist');
const indexFile = path.join(distDir, 'index.html');
const content = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>CalculadoraWebForms</title>
</head>
<body>
  <div id="root">CalculadoraWebForms frontend placeholder</div>
</body>
</html>
`;

fs.mkdirSync(distDir, { recursive: true });
if (!fs.existsSync(indexFile) || fs.readFileSync(indexFile, 'utf8') !== content) {
  fs.writeFileSync(indexFile, content, 'utf8');
}
console.log('frontend build complete');
