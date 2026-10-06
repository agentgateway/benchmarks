#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case "$(docker info --format '{{.Architecture}}')" in
  x86_64|amd64) mock_arch=amd64 ;;
  aarch64|arm64) mock_arch=arm64 ;;
  *) echo 'Unsupported Docker architecture' >&2; exit 1 ;;
esac
GOTOOLCHAIN=local CGO_ENABLED=0 GOOS=linux GOARCH="$mock_arch" go build -trimpath -o mock/mock-server mock/main.go
