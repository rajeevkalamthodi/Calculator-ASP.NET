import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen

import app


class ApplicationConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.config_path = Path(self.temporary.name) / "app_config.json"
        self.data = json.loads(app.CONFIG_PATH.read_text(encoding="utf-8"))
        self.data["runtime"] = {"host": "127.0.0.2", "port": 8127}
        self.data["ui"]["title"] = "Configured <Calculator>"
        self.data["ui"]["heading"] = "Configured heading"
        self.data["ui"]["labels"] = {
            "number1": "Configured first",
            "number2": "Configured second",
            "result": "Configured result",
        }
        self.data["ui"]["buttons"] = {
            operation: "Configured " + operation
            for operation in ("add", "subtract", "multiply", "divide", "power", "sqrt")
        }
        self.config_path.write_text(json.dumps(self.data), encoding="utf-8")

    def test_loads_all_configuration_fields_from_file(self):
        config = app.load_config(self.config_path)
        self.assertEqual(config.runtime_host, "127.0.0.2")
        self.assertEqual(config.runtime_port, 8127)
        self.assertEqual(config.title, "Configured <Calculator>")
        self.assertEqual(config.heading, "Configured heading")
        self.assertEqual(config.label_number1, "Configured first")
        self.assertEqual(config.label_number2, "Configured second")
        self.assertEqual(config.result_label, "Configured result")
        for operation in self.data["ui"]["buttons"]:
            self.assertEqual(getattr(config, "button_" + operation), "Configured " + operation)

    def test_file_configuration_supplies_runtime_bind_defaults(self):
        with patch.object(app, "APP_CONFIG", app.load_config(self.config_path)):
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(app.get_runtime_bind(), ("127.0.0.2", 8127))

    def test_explicit_environment_overrides_runtime_defaults(self):
        with patch.object(app, "APP_CONFIG", app.load_config(self.config_path)):
            with patch.dict(os.environ, {"HOST": "127.0.0.1", "PORT": "9127"}, clear=True):
                self.assertEqual(app.get_runtime_bind(), ("127.0.0.1", 9127))

    def test_loaded_configuration_is_applied_to_http_page(self):
        with patch.object(app, "APP_CONFIG", app.load_config(self.config_path)):
            server = app.create_server("127.0.0.1", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(f"http://127.0.0.1:{server.server_port}/", timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    page = response.read().decode("utf-8")
                self.assertIn("<title>Configured &lt;Calculator&gt;</title>", page)
                self.assertIn("<h1>Configured heading</h1>", page)
                for value in self.data["ui"]["labels"].values():
                    self.assertIn(value, page)
                for value in self.data["ui"]["buttons"].values():
                    self.assertIn(value, page)
                self.assertIn('id="configRuntimeHost">127.0.0.2</span>', page)
                self.assertIn('id="configRuntimePort">8127</span>', page)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())

    def test_missing_configuration_fails_explicitly(self):
        with self.assertRaises(FileNotFoundError):
            app.load_config(Path(self.temporary.name) / "missing.json")

    def test_malformed_configuration_fails_explicitly(self):
        self.config_path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            app.load_config(self.config_path)

    def test_incomplete_configuration_fails_explicitly(self):
        self.config_path.write_text("{}", encoding="utf-8")
        with self.assertRaises(KeyError):
            app.load_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
