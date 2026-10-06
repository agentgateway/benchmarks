# Initial Gateway API comparison

This is the historical October 1, single-run campaign. For the completed
three-pass agentgateway v1.6.0 and Praxis release/nightly comparison, start with
[the current CPU reports](../cpu-comparison/2026-10-05-stable-comparison/README.md).

This is a companion to the CPU AI proxy campaign. It uses the community
[howardjohn/gateway-api-bench](https://github.com/howardjohn/gateway-api-bench)
suite and the standardized Gateway API v1.5.1 core HTTP conformance tests.
It is separate from GPU inference and from the AI-specific mock workload.

The [Praxis campaign patch](praxis-campaign.patch) applies to upstream revision
`141add64d25455a6acb7ea7c69e1e813bb05e339` using `git am`. It adds current
agentgateway/Praxis installation, resource/image provenance, bounded sequential
campaigns, backend/load-tool image overrides, readiness checks and validation of
raw Fortio results. Read its `CAMPAIGN.md` for installation and test semantics.
The patch is included for reproduction; it is not merged upstream.

Both implementations passed the same 33 core HTTP conformance tests. The [initial reports and complete raw evidence](results/2026-10-01-initial/README.md)
cover direct-service and paired gateway traffic, lifecycle and scale/churn. Do not infer a performance
score from a test command's exit status: the original benchtool wrapper can
return success after Fortio aborts. Failures, missing measurements and resource
limits must remain visible.
