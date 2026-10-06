# CPU gateway comparisons

These Solo.io evaluations separate protocol correctness, forwarding/native-AI
performance, configuration lifecycle and source-supported capabilities. They are
not independent certification or GPU inference benchmarks.

| Campaign | Versions and scope | Read first |
| --- | --- | --- |
| October 5 stable comparison | Agentgateway v1.6.0; Praxis core v0.5.2 and nightly-20261002; Praxis AI v0.5.0 and October 2 nightly. Three repetitions of every completed CPU workload; direct baselines, resource observations and lifecycle evidence. | [Current comparison](2026-10-05-stable-comparison/README.md) |
| October 2 extended Gateway API | Same agentgateway and core pins, conformance v1.5.1. Three repetitions per core pairing; stock nightly setup-blocked. | [Exact case outcomes](2026-10-02-gateway-extended/README.md) |

The current campaign's corrected static-address test uses conformance v1.6.1 and
remains a separate follow-up. Do not splice it into the earlier 107-case score or
pool campaigns into extra repetitions. Core and AI distributions remain separate
throughout; inspect the full workload matrix before using a favorable ratio.
