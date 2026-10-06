from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Calculadora Web Forms</title>
</head>
<body>
  <h1>Calculadora Web Forms</h1>
  <p>Static build artifact for discovered frontend verification.</p>
</body>
</html>
"""


def main() -> None:
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(HTML, encoding="utf-8")


if __name__ == "__main__":
    main()
