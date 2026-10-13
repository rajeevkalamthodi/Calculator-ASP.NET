import json
import unittest
from pathlib import Path


class ConfigurationMetadataTests(unittest.TestCase):
    def test_example_config_exposes_project_metadata_defaults(self):
        config = json.loads(Path("config.example.json").read_text(encoding="utf-8"))
        self.assertEqual(config["visualStudioVersion"], "10.0")
        self.assertEqual(
            config["vSToolsPath"],
            "C:\\Program Files (x86)\\MSBuild\\Microsoft\\VisualStudio\\v10.0",
        )
        self.assertIn("WebApplications", config["webApplicationTargetsProject"])


if __name__ == "__main__":
    unittest.main()
