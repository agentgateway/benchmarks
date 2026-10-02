# Initial CPU-only Gateway API evidence

One observation per configuration on October 1, 2026 (execution timestamps are October 2 UTC). This Solo.io evaluation compares agentgateway v1.5.0 with Praxis operator `fb8beaa` and its documented core 0.5.2, plus a direct Service baseline. It is not a third-party certification or a GPU inference test.

- [Agentgateway versus direct Service](agentgateway-vs-service.md)
- [Praxis versus agentgateway](praxis-vs-agentgateway.md)
- [Shared core HTTP conformance](conformance.md)
- [Route lifecycle and scale/churn](lifecycle.md)
- [Sampled resource summary](resources.json)
- [Reproduction and exact component/resource settings](../../REPRODUCE.md)

`raw.tar.gz` contains complete conformance attempts, initial qualification failures, traffic measurements and aborts, lifecycle logs, scale snapshots, sampled kubelet resource data and final cluster state. It also retains the documented core 0.5.2 qualification alongside the separate newer core 0.7.2 empty-Gateway startup failure. Earlier invalid conformance invocations are explained in the conformance report, not scored as product failures. No measured attempt was removed to select a favorable result.

Verify and extract:

```sh
sha256sum -c SHA256SUMS
tar xzf raw.tar.gz
(cd gateway && sha256sum -c SHA256SUMS)
python3 ../../report.py --root gateway --output regenerated --evidence-link gateway
python3 ../../resources.py --root gateway --output resources-regenerated.json
python3 ../../summarize-scale.py gateway > scale-regenerated.json
```

The paired reports use successful QPS, retaining errors and unavailable measurements. All five 512-connection attempts aborted through the kind load balancer's descriptor limit; they do not provide throughput measurements. The 256 MiB Praxis OOM in the fixed-rate trial is included. A single-host shared-resource test and one measurement per case do not establish broad product rankings or confidence intervals.

The lifecycle intervals include setup and cleanup. Scale checkpoints inspect API status under synthetic object/configuration churn, not traffic success for thousands of real backends. Sampled working-set maxima are neither true memory peaks nor per-process RSS. See the report for per-case semantics and limitations.
