import unittest

from calculator_app import calculate
from pathlib import Path
import json


class InvariantTests(unittest.TestCase):
    def test_multiplication_result_matches_product_of_inputs(self):
        self.assertEqual(calculate("multiplicar", "7", "6"), "42")
        self.assertEqual(calculate("multiplicar", "2.5", "4"), "10")

    def test_configuration_metadata_keeps_csharp_targets_always_imported(self):
        config = json.loads(Path("config.example.json").read_text(encoding="utf-8"))
        self.assertEqual(
            config["cSharpTargetsProject"],
            "$(MSBuildBinPath)\\Microsoft.CSharp.targets",
        )
        self.assertIn("WebApplications", config["webApplicationTargetsProject"])


if __name__ == "__main__":
    unittest.main()
