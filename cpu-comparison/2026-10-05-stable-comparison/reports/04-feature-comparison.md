# Feature comparison at the tested revisions

The benchmark measures specific configurations. This capability review adds
source context without treating untested features as passed tests. **Observed**
means qualification or a linked campaign exercised that behavior; **source**
means the pinned implementation/documentation describes it. A configuration
failure is a result for the tested component pairing, not a verdict on every
possible deployment.

## Components and versions

| Component | Revision used | Role in this comparison |
| --- | --- | --- |
| agentgateway v1.6.0 | `ea5608642b9d` | Integrated data plane; matching v1.6.0 Kubernetes controller |
| Praxis core v0.5.2 | `af54edcd24de` | Standalone forwarding and stock operator-managed Gateway API |
| Praxis core nightly-20261002 | `31ac6dc86fba` | Standalone forwarding; stock operator pairing tested separately |
| Praxis AI v0.5.0 | `2f8732c1389b` | Native AI protocols/translation; separate distribution |
| Praxis AI October 2 nightly | `f5f51a751d6f` | Native AI profile; separately verified scheduled build |
| Praxis operator | `fb8beaa14cf7` | Latest upstream HEAD rechecked October 5; no newer release found |

The AI release's lockfile uses core libraries **0.7.2**, not 0.5.2. Its version
must appear explicitly beside native-AI results. The October 2 AI nightly was
recovered via its SHA tag and verified against the scheduled build digest; AI
does not use the core project's dated tag convention. [Nightly provenance](../evidence/versions/praxis-ai-nightly-provenance.json). [AI dependency lockfile](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/Cargo.lock),
[exact image identities](../evidence/versions/selection.json).

## What this campaign exercises

| Capability | agentgateway v1.6.0 | Praxis core v0.5.2 | Praxis core nightly-20261002 | Praxis AI v0.5.0 | Praxis AI October 2 nightly |
| --- | --- | --- | --- | --- | --- |
| Plain HTTP forwarding | Observed, common profile | Observed, common profile | Observed, common profile | Outside the separate native profile | Outside the separate native profile |
| OpenAI/Anthropic JSON and SSE forwarding | Observed, common and native profiles | Observed as transport | Observed as transport | Observed through native filters | Observed through native filters |
| Upstream stream cancellation | Observed in qualification | Observed in qualification | Observed in qualification | Observed in qualification | Observed in qualification |
| Anthropic-to-Chat-Completions translation | Observed, native profile | Not supplied by the reviewed core AI filter inventory | Not supplied by the reviewed core AI filter inventory | Observed, native profile | Observed, native profile |
| Token usage/accounting | LLM pipeline configured; accounting accuracy not independently audited | Not tested as native AI functionality | Not tested as native AI functionality | Response-usage extraction configured; accounting accuracy not independently audited | Same response-usage extraction configuration; accuracy not independently audited |
| Stock Kubernetes controller/data-plane startup | Observed | Observed | Blocked: generated cluster name rejected | AI image not used by the operator campaign | AI image not used by the operator campaign |
| Gateway API extended cases | See retained per-case evidence | See retained per-case evidence | Setup blocked in retained conformance campaign | Not evaluated | Not evaluated |
| GPU inference efficiency or model quality | Paused, not measured | Paused, not measured | Paused, not measured | Paused, not measured | Paused, not measured |

The [scope document](../docs/COMPARISON-SCOPE.md) explains common versus native
work. Passing protocol fixtures does not establish all OpenAI/Anthropic API
operations, every streaming event combination, or resilience against malformed
input. Performance conclusions require the final reviewed three-pass reports.

For a requirement-oriented view of the retained exact conformance cases, see
[requirements and evidence](requirements-index.md).

## Source-supported differences worth evaluating

| Area | agentgateway v1.6.0 | Praxis at the pinned revisions | Evidence boundary |
| --- | --- | --- | --- |
| Deployment model | Rust data plane and Go Kubernetes controller in one project | Core proxy, AI distribution and Rust operator are separate components | Integration effort was not quantitatively measured |
| Provider/API breadth | Provider integrations include OpenAI, Anthropic, Gemini, Bedrock and others | AI release has provider-specific classification, transformation and usage filters | This campaign exercises two API shapes and one translation pair |
| Gateway-owned Responses/Conversations state | No corresponding native state service identified in the reviewed scope; provider forwarding and budget databases are different functions | AI release explicitly implements response history, rehydration and Conversations; published `full` profile includes PostgreSQL; SQLite requires its build feature | Storage, authorization and multi-replica behavior not benchmarked |
| MCP | Federation, tool mediation, multiple transports and OAuth are documented | AI `mcp` stateless profile routes `tools/call`; its current/session profile explicitly returns `-32601` for that operation; Responses MCP dispatch is another path | No MCP interoperability campaign was run; avoid a single “MCP supported” score |
| A2A | Integrated A2A handling documented | AI filter classifies requests and routes task/context follow-ups using a local store | Restart/multi-replica task continuity not tested |
| Prompt/content guards | Applicability includes Completions, Messages, Responses and Gemini; excludes several other input formats | AI external guardrail filter documents Chat Completions request/response support; do not extend it automatically to Messages, Responses or MCP | Efficacy and policy overhead not measured |
| Authorization/policy extension | Native CEL/authentication plus external authorization/processing integrations | Core v0.5.2 exposes opt-in `cpex-policy-engine`; nightly defaults include the newer `policy-engine`; AI release enables policy in its `full` profile | Source/build defaults, not a security certification or runtime policy test |
| Budget/admission semantics | Standalone budget accounting charges reported usage after responses; missing usage cannot be charged through that path | AI token-rate-limit feature is experimental and opt-in; separate from ordinary response token extraction | No hard global spending-bound comparison was performed |
| Inference endpoint selection | Controller supports InferencePool; standalone endpoint-picker routing is also documented | AI has an optional llm-d-specific ext_proc integration behind `llmd-ext-proc`, outside its `full` feature set | Source capability only; EPP behavior and GPU inference efficiency were not measured |
| Configuration delivery | Kubernetes controller supplies data-plane configuration dynamically | Reviewed operator generates ConfigMaps and changes deployment configuration hashes; native core reload is a separate mechanism | Use measured route/restart results rather than assuming equivalent update behavior |

Pinned sources for these rows:

- [agentgateway overview](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/README.md), [provider/API and guard applicability](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/crates/llm/src/lib.rs), [budget semantics](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/crates/agentgateway/src/http/budget/mod.rs).
- [Praxis AI feature/build profiles](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/docs/features.md), [server features](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/server/Cargo.toml), [MCP profiles](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/docs/filters/mcp.md), [A2A routing](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/docs/filters/a2a.md), [AI guardrails](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/docs/filters/ai_guardrails.md), [token usage extraction](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/docs/filters/token_count.md).
- [Core v0.5.2 build features](https://github.com/praxis-proxy/praxis/blob/af54edcd24de01e4dac7da59a809bf88bd246fe5/server/Cargo.toml), [nightly build features](https://github.com/praxis-proxy/praxis/blob/31ac6dc86fba30ff510b17f9139021de60d8ba79/crates/server/Cargo.toml), [operator configuration delivery](https://github.com/praxis-proxy/operator/blob/fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c/src/controller/gateway.rs).

## Fair interpretation

Agentgateway's broader retained Gateway API results are evidence about the
selected tests and versions. They do not settle every AI use case. Praxis AI's
stateful APIs and composable policy/filter model are substantive capabilities,
with operational responsibilities that this performance campaign does not test.
Conversely, core forwarding performance does not establish native AI feature
parity. Choose the report matching the deployment and workload, and keep the
source-supported differences alongside the measured evidence.

## Release and project boundaries

The pinned root license declarations also differ by distribution and revision:
agentgateway is [Apache-2.0](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/LICENSE),
Praxis core v0.5.2 is [MIT](https://github.com/praxis-proxy/praxis/blob/af54edcd24de01e4dac7da59a809bf88bd246fe5/LICENSE),
and core nightly is [Apache-2.0](https://github.com/praxis-proxy/praxis/blob/31ac6dc86fba30ff510b17f9139021de60d8ba79/LICENSE).
Both pinned AI builds declare Apache-2.0 in their root license and workspace
metadata. [AI release license](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/LICENSE),
[AI nightly license](https://github.com/praxis-proxy/ai/blob/f5f51a751d6f25acde96fb840665b24f2696ce46/LICENSE).
These are source declarations, not a transitive dependency license inventory;
the [retained file hashes](../evidence/versions/root-license-declarations.json)
identify the exact review inputs.

Agentgateway's pinned tree includes a [project charter](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/CHARTER.md)
and [security policy](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/SECURITY.md).
Praxis core has [governance](https://github.com/praxis-proxy/praxis/blob/31ac6dc86fba30ff510b17f9139021de60d8ba79/GOVERNANCE.md),
[maintainer](https://github.com/praxis-proxy/praxis/blob/31ac6dc86fba30ff510b17f9139021de60d8ba79/MAINTAINERS.md),
and [security](https://github.com/praxis-proxy/praxis/blob/31ac6dc86fba30ff510b17f9139021de60d8ba79/SECURITY.md)
documents; AI has its own [maintainer](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/.github/MAINTAINERS.md)
and [security](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/.github/SECURITY.md)
documents. Their presence is not a measured support SLA, adoption count or security
ranking. Operational evaluations should separately check supported component
combinations, upgrade compatibility and the support arrangements a buyer needs.

## October 2 AI nightly delta

The AI nightly `f5f51a751d6f` is one commit ahead of release `2f8732c1389b`.
The [pinned source comparison](https://github.com/praxis-proxy/ai/compare/2f8732c1389b889660bcb3495af4d4d28dd4e682...f5f51a751d6f25acde96fb840665b24f2696ce46)
changes Responses compaction/state preservation and related tests/documentation.
The dependency lockfile, server build features, feature overview and token-usage
filter documentation are byte-identical between the reviewed archives. Both
therefore use the same core library version, while their images remain distinct.

Native Chat Completions, Anthropic Messages, translation, SSE and cancellation
are independently qualified and measured for each image. This campaign does not
exercise the Responses compaction change, so it cannot certify that fix or infer
stateful API correctness from similar native-profile throughput. The source-level
AI capabilities above apply to both reviewed builds unless noted; their runtime
results remain separate rows.

## Interpreting the stock operator's route-scale constraints

Praxis core v0.5.2 defines `MAX_FILTERS_PER_CHAIN` as a compile-time constant of
100 in its [pinned validator](https://github.com/praxis-proxy/praxis/blob/af54edcd24de01e4dac7da59a809bf88bd246fe5/core/src/config/validate/filter_chain.rs).
The filter-bearing HTTPRoute shape can make the stock operator generate one
chain with more entries than this guard permits. This source fact helps attribute
retained startup/reload errors; it does not establish a limit on bare routes or
prove that a different configuration representation would fail.

The generated ConfigMap's size is a separate delivery constraint. Final route
reports retain each attempted mutation and its diagnostics. Increasing pod memory
would not change either the compiled validator or Kubernetes's ConfigMap size
limit. A follow-up with changed product code or generated configuration must be
labeled as a different profile and requalified.

## Inference-routing integration is a separate evaluation

Both projects have endpoint-picker integration paths. Agentgateway v1.6.0 includes
InferencePool translation in its controller and a standalone endpoint-picker
configuration. The standalone example documents passthrough versus locally
validated destinations and fail-closed behavior; those standalone semantics
should not be generalized to every controller policy.
[Controller fixture](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/controller/pkg/agentgateway/translator/testdata/routes/inferencepool.yaml),
[standalone example](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/examples/llm-standalone-epp/README.md).

Praxis AI's integration is explicitly scoped to llm-d, rather than general
ext_proc compatibility. Its example combines an external processor with an
endpoint selector and strips the selected-destination header. It requires the
optional `llmd-ext-proc` Cargo feature, which is not included in `full`; the
reviewed Containerfile defaults to `full`, and the nightly publishing workflow
does not override that argument. This is a build-profile distinction, not an
absence of integration source. The integration documentation describes tests
using a mock ExternalProcessor and inference simulator, and explicitly excludes
proof of real EPP scheduling behavior. These reviewed files are identical in the
AI release and October 2 nightly.
[Integration scope](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/integrations/llmd/ext-proc/src/lib.rs),
[test boundary](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/docs/developing/llmd-integration-testing.md),
[build features](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/server/Cargo.toml),
[Containerfile](https://github.com/praxis-proxy/ai/blob/2f8732c1389b889660bcb3495af4d4d28dd4e682/Containerfile),
[nightly workflow](https://github.com/praxis-proxy/ai/blob/f5f51a751d6f25acde96fb840665b24f2696ce46/.github/workflows/publish.yaml),
[retained file hashes](../evidence/versions/inference-routing-source-review.json).

The CPU campaign enables neither integration. A future inference comparison
needs explicit build features, a pinned real EPP, matched scheduling policy and
model servers, correctness under EPP failure, and accelerator/SLO measurements.
GPU testing remains paused; forwarding or synthetic TTFT cannot answer those
questions.
