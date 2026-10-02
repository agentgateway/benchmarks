#!/usr/bin/env bash
# Build the pinned experimental llm-d integration. Never pushes an image.
set -euo pipefail

SOURCE_REVISION=f5f51a751d6f25acde96fb840665b24f2696ce46
LOCK_SHA256=32decbcebee5e611c1c75b08759391442e626e25b19196991ce7545d5f4c088a
FEATURES=full,llmd-ext-proc

if [[ $# -ne 2 ]]; then
  echo "usage: $0 PRAXIS_AI_SOURCE_DIR OUTPUT_IMAGE_TAG" >&2
  exit 2
fi
source_dir="$(cd "$1" && pwd)"
image_tag="$2"
[[ "$(git -C "${source_dir}" rev-parse HEAD)" == "${SOURCE_REVISION}" ]] || {
  echo "Praxis AI source must be checked out at ${SOURCE_REVISION}" >&2; exit 2;
}
[[ -z "$(git -C "${source_dir}" status --porcelain)" ]] || {
  echo "Praxis AI source must be clean, including untracked files" >&2; exit 2;
}
[[ "$(shasum -a 256 "${source_dir}/Cargo.lock" | cut -d ' ' -f 1)" == "${LOCK_SHA256}" ]] || {
  echo "Praxis Cargo.lock differs from the pinned lockfile" >&2; exit 2;
}
containerfile="$(mktemp "${TMPDIR:-/tmp}/praxis-benchmark-Containerfile.XXXXXX")"
trap 'rm -f -- "${containerfile}"' EXIT
# Keep the full workspace so --locked does not prune workspace members from
# Cargo.lock. The upstream cache recipe removes them and is unsuitable for a
# strict lockfile build. Retain its runtime stage and license notices verbatim.
python3 - "${source_dir}/Containerfile" "${containerfile}" <<'PYTHON'
from pathlib import Path
import sys
source = Path(sys.argv[1]).read_text()
runtime = source[source.index("FROM alpine:3.24\n"):]
builder = """FROM rust:1.98-alpine3.24 AS builder
ARG PRAXIS_AI_FEATURES=full,llmd-ext-proc
ENV RUSTFLAGS="-C target-feature=-crt-static"
RUN apk add --no-cache musl-dev openssl-dev pkgconf cmake make g++
WORKDIR /src
COPY . .
RUN cargo build --locked --release -p praxis-ai-proxy --no-default-features --features "${PRAXIS_AI_FEATURES}" \\
    && cp target/release/praxis-ai /usr/local/bin/praxis-ai
"""
Path(sys.argv[2]).write_text(builder + "\n" + runtime)
PYTHON
docker build --platform "${PRAXIS_BUILD_PLATFORM:-linux/amd64}" \
  --file "${containerfile}" --tag "${image_tag}" \
  --build-arg "PRAXIS_AI_FEATURES=${FEATURES}" \
  --label "org.opencontainers.image.revision=${SOURCE_REVISION}" \
  --label "dev.agentgateway.benchmark.praxis.features=${FEATURES}" \
  --label "dev.agentgateway.benchmark.praxis.cargo-lock-sha256=${LOCK_SHA256}" \
  "${source_dir}"
docker image inspect "${image_tag}" --format '{{json .}}'
echo "Built ${image_tag}. Push to your registry, record its digest, and set PRAXIS_IMAGE=repository@sha256:digest." >&2
