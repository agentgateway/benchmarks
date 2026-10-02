#!/usr/bin/env python3
"""Generate publishable inference comparison reports from one campaign."""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path

import yaml

from adapters.llm_d_benchmark import read_treatment
from common.model import validate_comparison
from common.plotting import plot_latency, plot_throughput, plot_ttft_p90
from common.rendering import write_csv, write_markdown


SUPPORTED_FORMATS = {"markdown", "png", "csv", "prism"}


def parse_comparison(value: str) -> tuple[str, str]:
    parts = value.split(":", 1)
    if len(parts) != 2 or not all(parts):
        raise argparse.ArgumentTypeError("comparison must be BASELINE:CANDIDATE")
    return parts[0], parts[1]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--campaign", required=True, type=Path)
    result.add_argument("--comparison", required=True, action="append", type=parse_comparison)
    result.add_argument("--formats", default="markdown,png,csv")
    result.add_argument("--output", type=Path)
    return result


def reset_generated_files(report_dir: Path) -> None:
    for name in (
        "README.md",
        "metrics.csv",
        "throughput_vs_qps.png",
        "latency_vs_qps.png",
        "ttft_p90_vs_qps.png",
    ):
        target = report_dir / name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"refusing unexpected generated artifact: {target}")
        if target.exists():
            target.unlink()


def write_prism_bundle(campaign: Path, output_root: Path, treatments: set[str]) -> None:
    prism_root = output_root / "prism"
    prism_root.mkdir(parents=True, exist_ok=True)
    for treatment in sorted(treatments):
        source = campaign / "runs" / treatment
        destination = prism_root / treatment
        if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
            raise ValueError(f"refusing unexpected Prism destination: {destination}")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)


def validate_registered_repetitions(
    campaign: Path, treatment: str, entry: object
) -> None:
    if not isinstance(entry, dict):
        raise ValueError(f"campaign treatment {treatment!r} is not a mapping")
    expected = set((entry.get("repetitions") or {}).keys())
    actual = {
        path.name.removeprefix("repetition-")
        for path in (campaign / "runs" / treatment).glob("repetition-*")
        if path.is_dir()
    }
    if actual != expected:
        raise ValueError(
            f"treatment {treatment!r} repetition artifacts do not match the "
            f"campaign manifest: manifest={sorted(expected)}, artifacts={sorted(actual)}"
        )


def validate_praxis_comparison(manifest: dict, baseline: str, candidate: str) -> None:
    """Refuse to publish a Praxis comparison with missing or unequal controls."""
    if "praxis-standalone" not in (baseline, candidate):
        return
    treatments = manifest["treatments"]
    praxis_runs = treatments["praxis-standalone"]["repetitions"]
    builds = set()
    for run in praxis_runs.values():
        gateway = run.get("gateway", {})
        image = gateway.get("image", "")
        source = gateway.get("source_revision", "")
        if not re.fullmatch(r"[^\s@]+@sha256:[0-9a-f]{64}", image):
            raise ValueError("Praxis comparison requires an immutable image digest")
        if not re.fullmatch(r"[0-9a-f]{40}", source):
            raise ValueError("Praxis comparison requires a source revision")
        if gateway.get("build_features") != "full,llmd-ext-proc":
            raise ValueError("Praxis comparison requires full,llmd-ext-proc build evidence")
        builds.add((image, source))
    if len(builds) != 1:
        raise ValueError("Praxis image/source must remain fixed across repetitions")
    if not all(name.endswith("-standalone") for name in (baseline, candidate)):
        return
    controls = set()
    for treatment in (baseline, candidate):
        for run in treatments[treatment]["repetitions"].values():
            digest = run.get("router_chart_digest", "")
            invariant = run.get("standalone_invariant_sha256", "")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                raise ValueError("standalone comparison requires the router chart digest")
            if not re.fullmatch(r"[0-9a-f]{64}", invariant):
                raise ValueError("standalone comparison requires the configuration invariant")
            controls.add((run.get("router_chart_version"), digest, invariant))
    if len(controls) != 1:
        raise ValueError("standalone comparison has different charts, EPP policies, resources or workloads")


def main() -> None:
    args = parser().parse_args()
    campaign = args.campaign.resolve()
    manifest_path = campaign / "campaign-manifest.yaml"
    if not manifest_path.is_file():
        raise ValueError(f"missing campaign manifest: {manifest_path}")
    with manifest_path.open(encoding="utf-8") as stream:
        manifest = yaml.safe_load(stream) or {}
    if manifest.get("suite") != "llm-d-benchmark":
        raise ValueError(f"unsupported report suite: {manifest.get('suite')!r}")

    formats = {value.strip() for value in args.formats.split(",") if value.strip()}
    unknown = formats - SUPPORTED_FORMATS
    if unknown:
        raise ValueError(f"unsupported report format(s): {', '.join(sorted(unknown))}")
    output_root = (args.output or campaign / "generated").resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, output_root / "campaign-manifest.yaml")

    generated: list[tuple[str, str, Path]] = []
    prism_treatments: set[str] = set()
    registered_treatments = manifest.get("treatments", {})
    for baseline_name, candidate_name in args.comparison:
        for treatment in (baseline_name, candidate_name):
            if treatment not in registered_treatments:
                raise ValueError(
                    f"treatment {treatment!r} is not registered in the campaign manifest"
                )
            validate_registered_repetitions(
                campaign, treatment, registered_treatments[treatment]
            )
        validate_praxis_comparison(manifest, baseline_name, candidate_name)
        prism_treatments.update((baseline_name, candidate_name))
        baseline = read_treatment(campaign, baseline_name)
        candidate = read_treatment(campaign, candidate_name)
        validate_comparison(baseline, candidate)
        report_dir = output_root / f"{baseline_name}-vs-{candidate_name}"
        report_dir.mkdir(parents=True, exist_ok=True)
        reset_generated_files(report_dir)
        if "csv" in formats:
            write_csv(report_dir / "metrics.csv", baseline, candidate)
        if "png" in formats:
            plot_throughput(baseline, candidate, report_dir / "throughput_vs_qps.png")
            plot_latency(baseline, candidate, report_dir / "latency_vs_qps.png")
            plot_ttft_p90(baseline, candidate, report_dir / "ttft_p90_vs_qps.png")
        if "markdown" in formats:
            evidence = {
                name: os.path.relpath(campaign / "runs" / name, report_dir)
                for name in (baseline_name, candidate_name)
            }
            write_markdown(
                report_dir / "README.md",
                manifest,
                baseline,
                candidate,
                "png" in formats,
                evidence,
            )
        generated.append((baseline_name, candidate_name, report_dir))

    if "prism" in formats:
        write_prism_bundle(campaign, output_root, prism_treatments)

    if "markdown" in formats:
        lines = ["# Inference Benchmark Campaign", ""]
        lines.append(f"Campaign: `{manifest['campaign_id']}`")
        lines.extend(["", "## Comparisons", ""])
        for baseline, candidate, report_dir in generated:
            relative = report_dir.relative_to(output_root)
            lines.append(f"- [{baseline} vs {candidate}]({relative}/README.md)")
        lines.append("")
        (output_root / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
