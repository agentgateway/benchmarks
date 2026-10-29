from __future__ import annotations

import csv
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPORTING = Path(__file__).resolve().parents[1]
GENERATOR = REPORTING / "generate.py"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    return struct.unpack(">II", header[16:24])


def report(stage: int, rate: float, multiplier: float) -> dict:
    latency = {
        "time_to_first_token": {
            "mean": 0.3 * multiplier,
            "p50": 0.2 * multiplier,
            "p90": 0.5 * multiplier,
        },
        "inter_token_latency": {
            "mean": 0.045 * multiplier,
            "p50": 0.04 * multiplier,
        },
        "normalized_time_per_output_token": {
            "mean": 0.055 * multiplier,
            "p50": 0.05 * multiplier,
        },
    }
    return {
        "version": "0.2",
        "scenario": {
            "load": {"standardized": {"stage": stage, "rate_qps": rate}},
            "stack": [
                {
                    "standardized": {
                        "kind": "inference_engine",
                        "tool": "vllm",
                        "tool_version": "v0.27.1",
                    }
                }
            ],
        },
        "results": {
            "request_performance": {
                "aggregate": {
                    "latency": latency,
                    "requests": {"failures": 1, "total": 100},
                    "throughput": {
                        "input_token_rate": {"mean": 9000 * multiplier},
                        "output_token_rate": {"mean": 1000 * multiplier},
                        "total_token_rate": {"mean": 10000 * multiplier},
                        "request_rate": {"mean": 10 * multiplier},
                    },
                }
            }
        },
    }


def all_failed_report(stage: int, rate: float) -> dict:
    result = report(stage, rate, 1.0)
    aggregate = result["results"]["request_performance"]["aggregate"]
    aggregate["latency"] = {}
    aggregate["throughput"] = {}
    aggregate["requests"] = {"failures": 100, "total": 100}
    return result


class GenerateReportTest(unittest.TestCase):
    def create_campaign(
        self,
        root: Path,
        candidate_rate: float = 10,
        candidate_multiplier: float = 1.5,
    ) -> Path:
        campaign = root / "campaign"
        manifest = {
            "schema_version": 1,
            "campaign_id": "test-campaign",
            "suite": "llm-d-benchmark",
            "identity": {
                "scenario": "optimized-baseline",
                "cluster_provider": "gke",
                "accelerator_type": "gpu",
                "accelerator_model": "h100",
                "backend_type": "vllm",
                "model": "Qwen/Qwen3-32B",
                "replicas": 8,
                "tensor_parallelism": 2,
                "workload": "upstream-optimized-baseline.yaml",
                "workload_variant": "upstream",
            },
            "treatments": {
                "service": {"repetitions": {"1": {}}},
                "agentgateway-standalone": {"repetitions": {"1": {}}},
            },
        }
        campaign.mkdir(parents=True)
        (campaign / "campaign-manifest.yaml").write_text(
            yaml.safe_dump(manifest), encoding="utf-8"
        )
        for treatment, multiplier, measured_rate in (
            ("service", 1.0, 10),
            ("agentgateway-standalone", candidate_multiplier, candidate_rate),
        ):
            repetition = campaign / "runs" / treatment / "repetition-1"
            repetition.mkdir(parents=True)
            # Stage zero is a duplicate-rate warm-up and must not appear in the
            # generated CSV; the later stage wins.
            for stage, rate in ((0, measured_rate), (1, 3), (2, measured_rate)):
                path = repetition / (
                    f"benchmark_report_v0.2,_{treatment}_stage_{stage}_"
                    "lifecycle_metrics.json.yaml"
                )
                path.write_text(yaml.safe_dump(report(stage, rate, multiplier)), encoding="utf-8")
        return campaign

    def add_repetition(self, campaign: Path) -> None:
        manifest_path = campaign / "campaign-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        for treatment, entry in manifest["treatments"].items():
            entry["repetitions"]["2"] = {}
            treatment_dir = campaign / "runs" / treatment
            shutil.copytree(
                treatment_dir / "repetition-1", treatment_dir / "repetition-2"
            )
        manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    def test_rejects_changed_backend_stack_metadata_in_stage(self) -> None:
        for stage in (0, 1, 2):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                campaign = self.create_campaign(Path(directory))
                path = next(
                    (campaign / "runs" / "service" / "repetition-1").glob(
                        f"*_stage_{stage}_*"
                    )
                )
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
                document["scenario"]["stack"][0]["standardized"]["tool_version"] = "v0.28.0"
                path.write_text(yaml.safe_dump(document), encoding="utf-8")
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(GENERATOR),
                        "--campaign",
                        str(campaign),
                        "--comparison",
                        "service:agentgateway-standalone",
                        "--formats",
                        "csv",
                    ],
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("different stack metadata", completed.stderr)

    def test_rejects_changed_component_stack_metadata_in_stage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.create_campaign(Path(directory))
            for path in (campaign / "runs").rglob("benchmark_report_*.yaml"):
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
                document["scenario"]["stack"].append(
                    {
                        "standardized": {
                            "kind": "orchestrator",
                            "tool": "kubernetes",
                            "tool_version": "v1.34.0",
                        }
                    }
                )
                if path.parent.parent.name == "service" and "_stage_2_" in path.name:
                    document["scenario"]["stack"][1]["standardized"]["tool_version"] = "v1.35.0"
                path.write_text(yaml.safe_dump(document), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--campaign",
                    str(campaign),
                    "--comparison",
                    "service:agentgateway-standalone",
                    "--formats",
                    "csv",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("different stack metadata", completed.stderr)

    def test_rejects_changed_stack_metadata_across_repetitions(self) -> None:
        for stage in (0, 2):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                campaign = self.create_campaign(Path(directory))
                self.add_repetition(campaign)
                path = next(
                    (campaign / "runs" / "service" / "repetition-2").glob(
                        f"*_stage_{stage}_*"
                    )
                )
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
                document["scenario"]["stack"][0]["standardized"]["tool_version"] = "v0.28.0"
                path.write_text(yaml.safe_dump(document), encoding="utf-8")
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(GENERATOR),
                        "--campaign",
                        str(campaign),
                        "--comparison",
                        "service:agentgateway-standalone",
                        "--formats",
                        "csv",
                    ],
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("different stack metadata", completed.stderr)

    def test_accepts_consistent_stack_metadata_across_stages_and_repetitions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = self.create_campaign(root)
            self.add_repetition(campaign)
            for path in (campaign / "runs").rglob("benchmark_report_*.yaml"):
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
                stack = document["scenario"]["stack"]
                stack[0]["custom"] = {
                    "report": path.name, "repetition": path.parent.name
                }
                stack.append(
                    {
                        "standardized": {
                            "kind": "orchestrator",
                            "tool": "kubernetes",
                            "tool_version": "v1.34.0",
                        }
                    }
                )
                throughput = document["results"]["request_performance"]["aggregate"]["throughput"]
                if path.parent.name == "repetition-2":
                    stack.reverse()
                    throughput["output_token_rate"]["mean"] *= 2
                if "_stage_0_" in path.name:
                    throughput["output_token_rate"]["mean"] = 999999
                path.write_text(yaml.safe_dump(document), encoding="utf-8")
            output = root / "published"
            subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--campaign",
                    str(campaign),
                    "--comparison",
                    "service:agentgateway-standalone",
                    "--output",
                    str(output),
                    "--formats",
                    "markdown,csv,prism",
                ],
                check=True,
            )
            report_dir = output / "service-vs-agentgateway-standalone"
            with (report_dir / "metrics.csv").open(encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 4)
            for row in rows:
                self.assertIn(row["requested_qps"], ("3.0", "10.0"))
                expected = 1500 if row["treatment"] == "service" else 2250
                self.assertEqual(float(row["output_tokens_per_second"]), expected)
            markdown = (report_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("Backend image/version: `v0.27.1`", markdown)
            for treatment in ("service", "agentgateway-standalone"):
                for repetition in (1, 2):
                    prism_reports = list(
                        (output / "prism" / treatment / f"repetition-{repetition}").glob(
                            "benchmark_report_*.yaml"
                        )
                    )
                    self.assertEqual(len(prism_reports), 3)

    def test_generates_upstream_style_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = self.create_campaign(root)
            output = root / "published"
            subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--campaign",
                    str(campaign),
                    "--comparison",
                    "service:agentgateway-standalone",
                    "--output",
                    str(output),
                    "--formats",
                    "markdown,png,csv,prism",
                ],
                check=True,
            )
            report_dir = output / "service-vs-agentgateway-standalone"
            for name in (
                "README.md",
                "metrics.csv",
                "throughput_vs_qps.png",
                "latency_vs_qps.png",
                "ttft_p90_vs_qps.png",
            ):
                self.assertGreater((report_dir / name).stat().st_size, 0)
            throughput_width, throughput_height = png_size(
                report_dir / "throughput_vs_qps.png"
            )
            latency_width, latency_height = png_size(
                report_dir / "latency_vs_qps.png"
            )
            p90_width, p90_height = png_size(report_dir / "ttft_p90_vs_qps.png")
            self.assertGreater(throughput_width, throughput_height * 2.5)
            self.assertGreater(latency_width, latency_height * 2.5)
            self.assertLess(abs(p90_width - p90_height), 50)
            csv_bytes = (report_dir / "metrics.csv").read_bytes()
            self.assertEqual(csv_bytes.count(b"\n"), 5)
            self.assertNotIn(b"\r\n", csv_bytes)
            self.assertIn(
                "Backend image/version: `v0.27.1`",
                (report_dir / "README.md").read_text(encoding="utf-8"),
            )
            markdown = (report_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("agentgateway standalone", markdown)
            self.assertNotIn("Agentgateway", markdown)
            self.assertIn("<details>", markdown)
            self.assertIn("| Rate | k8s service (RR) Output", markdown)
            self.assertIn(
                "a stock Kubernetes Service that round-robins requests",
                markdown,
            )
            self.assertIn("(no EPP, no scoring)", markdown)
            self.assertIn("where RR means round-robin", markdown)
            self.assertIn("**agentgateway mode:**", markdown)
            self.assertIn("standalone request scheduler mode", markdown)
            self.assertIn(
                "https://agentgateway.dev/docs/standalone/latest/inference/",
                markdown,
            )
            self.assertIn("## Interpreting ITL", markdown)
            self.assertIn(
                "ITL measures token cadence only after the first response token",
                markdown,
            )
            self.assertIn(
                "Lower ITL therefore does not by itself mean better overall inference latency",
                markdown,
            )
            with (report_dir / "metrics.csv").open(encoding="utf-8") as stream:
                columns = next(csv.reader(stream))
            self.assertIn("input_tokens_per_second", columns)
            self.assertIn("total_tokens_per_second", columns)
            self.assertIn("ttft_mean_seconds", columns)
            prism_reports = list(
                (output / "prism" / "service" / "repetition-1").glob(
                    "benchmark_report_v0.2,*.yaml"
                )
            )
            self.assertEqual(len(prism_reports), 3)

    def test_uses_report_display_names(self) -> None:
        sys.path.insert(0, str(REPORTING))
        from common.rendering import agentgateway_mode_note, display_name

        self.assertEqual(
            display_name("agentgateway-standalone"), "agentgateway standalone"
        )
        self.assertEqual(
            display_name("agentgateway-gateway"), "agentgateway on Kubernetes"
        )
        gateway_note = agentgateway_mode_note("agentgateway-gateway")
        self.assertIsNotNone(gateway_note)
        self.assertIn("Kubernetes Gateway API mode", gateway_note)
        self.assertIn(
            "https://agentgateway.dev/docs/kubernetes/latest/llm/inference/",
            gateway_note,
        )

    def test_rejects_mismatched_qps_ladders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            campaign = self.create_campaign(Path(directory), candidate_rate=11)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--campaign",
                    str(campaign),
                    "--comparison",
                    "service:agentgateway-standalone",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("QPS ladders differ", completed.stderr)

    def test_omits_itl_explanation_when_service_itl_is_not_lower(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = self.create_campaign(root, candidate_multiplier=0.5)
            output = root / "published"
            subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--campaign",
                    str(campaign),
                    "--comparison",
                    "service:agentgateway-standalone",
                    "--output",
                    str(output),
                    "--formats",
                    "markdown",
                ],
                check=True,
            )
            markdown = (
                output / "service-vs-agentgateway-standalone" / "README.md"
            ).read_text(encoding="utf-8")
            self.assertNotIn("## Interpreting ITL", markdown)

    def test_represents_all_failed_stage_without_fabricated_latency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = self.create_campaign(root)
            failed = campaign / "runs" / "agentgateway-standalone" / "repetition-1" / (
                "benchmark_report_v0.2,_agentgateway-standalone_stage_2_"
                "lifecycle_metrics.json.yaml"
            )
            failed.write_text(
                yaml.safe_dump(all_failed_report(2, 10)), encoding="utf-8"
            )
            output = root / "published"
            subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--campaign",
                    str(campaign),
                    "--comparison",
                    "service:agentgateway-standalone",
                    "--output",
                    str(output),
                    "--formats",
                    "markdown,png,csv",
                ],
                check=True,
            )
            report_dir = output / "service-vs-agentgateway-standalone"
            with (report_dir / "metrics.csv").open(encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            failed_row = next(
                row
                for row in rows
                if row["treatment"] == "agentgateway-standalone"
                and row["requested_qps"] == "10.0"
            )
            self.assertEqual(failed_row["output_tokens_per_second"], "0.0")
            self.assertEqual(failed_row["requests_per_second"], "0.0")
            self.assertEqual(failed_row["ttft_p50_seconds"], "")
            self.assertEqual(failed_row["failure_rate"], "1.0")
            self.assertIn(
                "| 10 | 1,000 | 0 | 0.2 | n/a",
                (report_dir / "README.md").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
