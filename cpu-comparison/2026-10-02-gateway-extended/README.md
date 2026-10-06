# Extended Gateway API comparison: October 2

These are the retained three-repetition correctness results for agentgateway
**v1.6.0**, Praxis core **v0.5.2**, and core **nightly-20261002**, each with the
pinned controller/operator. They use upstream **conformance v1.5.1** and are
separate from the October 5 performance campaign and corrected static-address
follow-up. Solo.io ran the evaluation and contributes to agentgateway.

| Implementation | Repetition 1 | Repetition 2 | Repetition 3 |
| --- | --- | --- | --- |
| Agentgateway v1.6.0, release comparison | 106/107 | 106/107 | 106/107 |
| Praxis core v0.5.2 + operator fb8beaa | 52/107 | 52/107 | 52/107 |
| Agentgateway v1.6.0, separate nightly comparison | 106/107 | 106/107 | 106/107 |
| Praxis core nightly-20261002 + operator fb8beaa | Setup blocked | Setup blocked | Setup blocked |

Both runnable releases passed all **33 selected HTTP core cases** every time.
The full selection includes 107 top-level cases, not 107 distinct features or a
percentage of the specification. These evaluator-selected probes include
features beyond declared implementation support. They are not official vendor
certification. The nightly's blocked prerequisite is not a zero feature score.

Agentgateway's retained `GatewayStaticAddresses` failure used an old upstream
assertion with an eventual-consistency race. Its release CI ran and passed the
corrected test. Keep the old score unchanged and read the
[CI investigation](reports/agentgateway-static-address-follow-up.md).
The fresh corrected-suite check is reported separately in the
[October 5 campaign](../2026-10-05-stable-comparison/README.md).

## Read the exact cases

- [HTTP core](reports/matrix/http-core.md).
- [HTTP/Gateway extensions and backend TLS](reports/matrix/http-gateway-extended.md).
- [gRPC](reports/matrix/grpc.md).
- [TLS-dependent cases](reports/matrix/tls.md).
- [Release interpretation](reports/release-comparison.md) and
  [nightly compatibility](reports/nightly-compatibility.md).
- [Methods](reports/methodology.md), [validity](reports/infrastructure-validity.md),
  [reproduction](reports/reproduce.md), and [version pins](evidence/versions/selection.json).

Praxis receives credit for observed extensions such as host/path rewrites,
request/backend timeouts and WebSocket backend behavior. Passing negative TLS
configuration tests does not establish positive TLSRoute routing; conversely,
TLSRoute failures do not erase both products' successful HTTPRoute HTTPS test.
Suite duration reflects readiness/assertion waits and is not a speed benchmark.

## Raw evidence

The companion technical-evidence release supplies
`extended-gateway-api-results.tar.gz`, its SHA-256 manifest, and the credential
redaction ledger. Publication links will be added after upload verification.
The archive contains `results/`, `qualification/`, `diagnostics/`, and
`rejected-infrastructure/`. Excluded attempts are retained but never enter the
three-run means. Synthetic TLS fixture private keys are redacted; a ledger
records original and sanitized member hashes.

Extract the archive into this directory to resolve raw paths printed in the
reports and machine-readable data. The root `results/` directory is deliberately
excluded from Git; large raw outputs belong to the release asset.

For offline regeneration after verifying the archive checksum:

```sh
tar -xzf /path/to/extended-gateway-api-results.tar.gz
python3 harness/summarize.py .
python3 harness/aggregate.py
python3 harness/write-matrix.py
```

An [offline replay](evidence/reanalysis.json) reproduced both JSON files and all four matrices byte-for-byte from the sanitized public archive. Compare your generated files with the committed copies. Do not treat
successful parsing as an independent scientific review. Upstream source links,
configuration, exact commands and the original validity decisions accompany the
results; operating a fresh cluster requires new qualification and review.
