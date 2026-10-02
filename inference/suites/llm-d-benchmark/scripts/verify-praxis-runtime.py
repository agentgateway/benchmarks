#!/usr/bin/env python3
"""Verify the actual Praxis sidecar and retain its immutable runtime evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify(document: dict, image: str, source_revision: str) -> dict:
    matches = []
    for pod in document.get("items", []):
        containers = pod.get("spec", {}).get("containers", [])
        for container in containers:
            if container.get("name") != "praxis-proxy":
                continue
            if container.get("image") != image:
                raise ValueError("running Praxis image differs from PRAXIS_IMAGE")
            if pod.get("status", {}).get("phase") != "Running":
                raise ValueError("Praxis pod is not Running")
            if not any(c.get("name") == "epp" for c in containers):
                raise ValueError("Praxis must share a pod with the EPP")
            if any(c.get("name") in ("envoy-proxy", "agentgateway-proxy") for c in containers):
                raise ValueError("unexpected second proxy in the Praxis pod")
            statuses = {c["name"]: c for c in pod.get("status", {}).get("containerStatuses", [])}
            status = statuses.get("praxis-proxy", {})
            if not status.get("ready") or not status.get("imageID"):
                raise ValueError("Praxis must be ready with an observed imageID")
            epp_status = statuses.get("epp", {})
            if not epp_status.get("ready") or not epp_status.get("imageID"):
                raise ValueError("EPP must be ready with an observed imageID")
            matches.append({
                "pod": pod["metadata"]["name"],
                "image": image,
                "image_id": status["imageID"],
                "epp_image_id": epp_status["imageID"],
                "declared_source_revision": source_revision,
                "required_build_features": "full,llmd-ext-proc",
                "containers": [{k: c[k] for k in ("name", "image", "resources", "command", "args") if k in c} for c in containers],
            })
    if len(matches) != 1:
        raise ValueError(f"expected one ready Praxis/EPP pod, found {len(matches)}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()
    result = verify(json.loads(args.input.read_text()), args.image, args.source_revision)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["pod"])


if __name__ == "__main__":
    main()
