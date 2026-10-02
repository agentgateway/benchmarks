from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/verify-praxis-runtime.py"
SPEC = importlib.util.spec_from_file_location("verify_praxis_runtime", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
IMAGE = "example.invalid/praxis@sha256:" + "a" * 64
REVISION = "b" * 40


class VerifyPraxisRuntimeTest(unittest.TestCase):
    def pod(self) -> dict:
        return {
            "metadata": {"name": "test-epp-0"},
            "spec": {"containers": [
                {"name": "praxis-proxy", "image": IMAGE},
                {"name": "epp", "image": "example.invalid/epp:v0.9.0"},
            ]},
            "status": {"phase": "Running", "containerStatuses": [
                {"name": "praxis-proxy", "ready": True, "imageID": IMAGE},
                {"name": "epp", "ready": True, "imageID": "example.invalid/epp@sha256:" + "c" * 64},
            ]},
        }

    def test_records_observed_image_and_declared_source_separately(self) -> None:
        evidence = MODULE.verify({"items": [self.pod()]}, IMAGE, REVISION)
        self.assertEqual(evidence["pod"], "test-epp-0")
        self.assertEqual(evidence["image_id"], IMAGE)
        self.assertEqual(evidence["declared_source_revision"], REVISION)

    def test_rejects_wrong_image_not_ready_missing_epp_and_extra_proxy(self) -> None:
        for mutation in ("image", "ready", "epp_ready", "epp", "extra"):
            with self.subTest(mutation=mutation):
                pod = self.pod()
                if mutation == "image":
                    pod["spec"]["containers"][0]["image"] = "praxis:latest"
                elif mutation == "ready":
                    pod["status"]["containerStatuses"][0]["ready"] = False
                elif mutation == "epp_ready":
                    pod["status"]["containerStatuses"][1]["ready"] = False
                elif mutation == "epp":
                    pod["spec"]["containers"].pop()
                else:
                    pod["spec"]["containers"].append({"name": "envoy-proxy"})
                with self.assertRaises(ValueError):
                    MODULE.verify({"items": [pod]}, IMAGE, REVISION)

    def test_rejects_missing_or_duplicate_praxis_pods(self) -> None:
        for pods in ([], [self.pod(), copy.deepcopy(self.pod())]):
            with self.assertRaises(ValueError):
                MODULE.verify({"items": pods}, IMAGE, REVISION)


if __name__ == "__main__":
    unittest.main()
