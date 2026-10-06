# Reproduce this campaign

Status: all three CPU and Kubernetes passes are reviewed; final evidence is
retained, and all eight campaign VMs/boot disks have been explicitly deleted.
Installed input hashes and review records are retained under `evidence/versions`
and `evidence/qualification`. See the campaign README for raw release assets.

## Prerequisites

Use this source snapshot, Python 3, Go, `gcloud`, SSH/SCP, `gh`, and authenticated
access to your approved GCP project. For the existing public raw artifacts, use [the public evidence guide](PUBLIC-EVIDENCE.md); private publication scripts describe the original administration workflow. Use fresh VM
names and an output directory that does not contain old results. The checked-in
scripts are fixed to the recorded project, zone and campaign prefix; change the
prefix consistently for a fresh reproduction and record that diff.

Read [network paths](TOPOLOGY.md), [protocol](PROTOCOL.md), and
[comparison scope](COMPARISON-SCOPE.md). Image
identities are in [selection.json](../evidence/versions/selection.json).
Praxis AI release v0.5.0 uses registry tag `0.5.0`; its amd64 digest is the
measurement pin. The October 2 AI nightly is independently pinned from its
scheduled publishing workflow and SHA tag. Neither is a core Praxis image.

## Standalone setup

Build `harness/mock/main.go` for Linux amd64 with CGO disabled into
`.work/mock-server`. Record its SHA-256; this run reused the byte-identical
previous fixture. `python3 infra/provision-ai.py` creates three disposable VMs,
installs tools, renders private addresses, creates stopped gateway containers,
and starts host collectors. Each VM has a 12-hour auto-delete fallback.

The GCP SDK initially establishes trusted SSH host keys. `infra/transport.py`
then uses the captured instance IDs, addresses, existing private-key path and
strict gcloud host-key verification for administration. Workloads never traverse
those external addresses. If an administration call times out, inspect the remote
unit and output directory before resuming; never blindly dispatch a duplicate.

Run `python3 infra/provision-native.py` to render and install the two native AI
configuration files, three stopped gateway containers and native client tools. The setup scripts disable inherited
Docker healthchecks; readiness is checked externally against the workload. Common and native
profiles must not run concurrently on these VMs.

## Qualification and first-pass gate

Run `python3 infra/run-common-pass.py qualification-nohealth` and inspect all protocol,
cancellation, load-generator, resource and image/config evidence. The label identifies the final seeded profile with inherited healthchecks disabled.
Earlier qualification artifacts remain historical checks, not accepted repetitions.
Run `python3 infra/run-native-pass.py qualification-nohealth` separately. Verify
AIPerf seed 42 and matching generated message contents, excluding session UUIDs.

Write reviewed qualification JSON with `infrastructure_valid: true` and
`aiperf_random_seed: 42` only after
attribution checks. Gate filenames are enforced in the corresponding runner.
Do not copy old approval files or treat an exit-zero marker as scientific review.
Run `python3 infra/run-cpu-pass.py pass1` to execute common then native sequentially.
Export results with `infra/export-cpu.py` into a fresh labeled snapshot. Inspect
all raw tool exits/errors and host samples before approving repetitions 2 and 3.
Do not dispatch either repeat until the complete Kubernetes first pass has also
been reviewed. The combined gate requires `pass1-review.json`,
`native-pass1-review.json`, and `kubernetes-pass1-review.json`, each with an
explicit `infrastructure_valid: true` decision and its supporting evidence.

## Kubernetes

The Kubernetes scripts create five additional native GCE nodes. They install
K3s, the pinned controllers, MetalLB's IP-allocation controller, and a deterministic
backend. The provisioner installs the uniform host TCP profile and chained CNI
tuning before workload pods start; existing pods must be recreated when applying
this profile to an existing cluster. There is no GKE cluster, managed GCP load balancer, or Envoy proxy.
MetalLB VIPs are internal test addresses; measured HTTP uses private NodePort.

Build the Gateway API test binary from the pinned source repository's
**conformance subdirectory**, which has its own Go module and a parent-module
replacement. Build the pinned ClusterLoader2 source and archive the unchanged
Praxis operator source. Place those inputs in `.work` as referenced by
`infra/provision-kubernetes.py`. Preserve binary/source checksums.

Create each role with `infra/create-kubernetes-vm.sh`, then run the provisioner.
The bootstrap recovery script `infra/finish-kubernetes.py` applies only after the
client tools and operator build have started on existing nodes; it creates no VMs.

Run `harness/run-kubernetes.py qualification-image-pin` on the dedicated Kubernetes client
under systemd with LimitNOFILE=65536. Inspect pod TCP settings, sustained 512-connection unlimited-rate traffic,
ten-route create/update, HTTP tool
and restart evidence, node placement, and the retained stable-single-pod/requested-image barrier. A reviewed remote qualification marker
is required for `pass1`; a separate first-pass review is required for `pass2` and
`pass3`. Do not turn a controller/data-plane setup failure into per-feature scores.

After an interrupted ClusterLoader2 run, capture any remaining `gwcmp-cl2-*`
namespaces and remove only those created by this campaign before requalification.
Do not bypass the tool's stale-namespace check or count that setup rejection as a
product failure.

The October 2 extended-conformance evidence remains a separate suite/version.
The corrected static-address follow-up uses upstream conformance v1.6.1 and its
pinned parent revision. Do not splice it into a fictitious 107-case rerun.

After first-pass approval, copy the Kubernetes review to the dedicated client as
`/opt/gateway-benchmark/kubernetes-pass1-approved.json`. Run
`python3 infra/run-remaining-cpu.py` and
`python3 infra/run-remaining-kubernetes.py` on the administration host. These
drivers use distinct VM groups and can run concurrently. The CPU driver executes
common then native profiles sequentially for each repeat; the Kubernetes driver
executes each repeat and its focused static-address follow-up sequentially.
Both refuse to start without all three local first-pass review records and
export their final snapshots on completion. A failed administrative call requires
inspection of the existing remote unit before any resume; do not rerun the
remaining-pass driver blindly against existing output directories.

## Analysis and cleanup

`harness/summarize-load.py` emits per-run metrics and three-pass aggregates from
immutable exported results. Review resource samples with `summarize-hosts.py`.
Nighthawk's nearest quantile above p99 is labeled an upper bracket; its in-flight
requests at cutoff are not automatically HTTP errors. AIPerf uses the deterministic
mock backend, not GPUs or a live inference provider.

Archive raw outputs and telemetry, redact credentials/generated fixture keys,
record SHA-256 manifests, and verify the retained export before deleting resources.
Run `infra/teardown.py` to delete only captured instance IDs with the campaign
ownership label and their boot disks. Confirm absence and remove temporary
kubeconfig/join-token files. Then publish private release assets and verify uploaded
hashes; a publication delay must not keep verified, no-longer-needed VMs running.
Auto-delete is a fallback, not the cleanup procedure.

## Exact tool builds

Use Go 1.26.4 and the retained source revisions. The mock and ClusterLoader2
binaries were reused byte-for-byte from the preceding CPU campaign; the
corrected conformance binary was built for this campaign. Build information and
hashes are in [tool-builds.json](../evidence/versions/tool-builds.json).
From this campaign directory, with fresh source directories:

```sh
mkdir -p .work
campaign_dir="$PWD"
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath \
  -o .work/mock-server harness/mock/main.go

git clone https://github.com/kubernetes/perf-tests .work/perf-tests
git -C .work/perf-tests checkout b337418289cce7ac518ed7e6920cded4a816e82c
(cd .work/perf-tests/clusterloader2 && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
  -trimpath -o "$campaign_dir/.work/clusterloader2" ./cmd/clusterloader.go)

git clone https://github.com/kubernetes-sigs/gateway-api .work/gateway-api
git -C .work/gateway-api checkout 8bb74df00e56ec8f944d48c25e6c1c9c2f6848e3
(cd .work/gateway-api/conformance && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
  go test -c -o "$campaign_dir/.work/gateway-conformance.test" .)

git clone https://github.com/praxis-proxy/operator .work/operator
git -C .work/operator archive --format=tar.gz \
  fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c \
  > .work/praxis-operator-source.tar.gz
```

Record `go version -m` and SHA-256 for every output. Toolchain, dependency or
image-base changes can alter rebuilt bytes; identify those differences rather
than silently claiming the original hash. Product image digests remain fixed.
The operator's permission-syntax adaptation for Docker's classic builder is
recorded in `infra/build-praxis-operator.sh`; Rust source is unchanged.

## No-cloud analysis path

Download the private release assets and verify
`SHA256SUMS` before extraction. Extract one final archive per role into an analysis
root named `client`, `gateway`, `backend`, `kclient`, `kgateway`, `kbackend`,
`kcontroller`, `kcontrol`. Do not combine multiple intermediate exports, which
would duplicate measurements. The release manifest will identify the final files.

```sh
python3 -m venv .work/analysis-venv
.work/analysis-venv/bin/pip install -r docs/analysis-requirements.txt
python3 harness/summarize-load.py ANALYSIS_ROOT --output reports/data
python3 harness/summarize-control.py ANALYSIS_ROOT/kclient --output reports/data
python3 harness/summarize-hosts.py ANALYSIS_ROOT \
  --output reports/data/cpu-host-workloads.json
python3 harness/summarize-hosts.py ANALYSIS_ROOT --suite gateway \
  --output reports/data/kubernetes-host-workloads.json
python3 harness/summarize-hosts.py ANALYSIS_ROOT --suite gateway --phases \
  --output reports/data/kubernetes-host-phases.json
```

The control report also uses the attributed lifecycle findings. Regenerate them
from the same snapshot before rendering, and retain the recovery-window audit:

```sh
python3 harness/review-kubernetes-attribution.py ANALYSIS_ROOT \
  --output evidence/qualification/final-facts/kubernetes-attribution.json
python3 harness/audit-recovery-overlap.py ANALYSIS_ROOT \
  --output evidence/qualification/final-facts/recovery-overlap.json
python3 harness/summarize-claims.py reports/data \
  --review evidence/qualification/final-review.json
python3 harness/render-load-reports.py reports/data --output reports \
  --review evidence/qualification/final-review.json
python3 harness/render-control-report.py reports/data \
  --output reports/03-gateway-api.md \
  --review evidence/qualification/final-review.json
python3 harness/render-resource-report.py reports/data \
  --cpu-hosts reports/data/cpu-host-workloads.json \
  --kubernetes-hosts reports/data/kubernetes-host-workloads.json \
  --output reports --review evidence/qualification/final-review.json
.work/analysis-venv/bin/python harness/plot-load.py reports/data \
  --output reports/figures --review evidence/qualification/final-review.json
```

The attribution reviewer asserts known retained outcomes. A fresh campaign with
different behavior needs a new manual review; changing assertions to accept an
expected winner would invalidate the comparison.

Report and plot generators require the retained final manual review, including
`infrastructure_valid` and `all_three_passes_reviewed`. This guard prevents an
incomplete export from silently producing a three-run report. Plotting dependencies
are separate from the VM load-generator environment. Review [evidence layout](EVIDENCE-LAYOUT.md)
and [review gates](REVIEW-CHECKLIST.md) before regenerating claims.

For the campaign's retained final snapshots, `infra/prepare-analysis.py` assembles
one copy per role and `infra/review-final-facts.py` collects all three passes'
load, isolation, startup, resource and control facts. The latter does not approve
results. After manual review, use `harness/render-load-reports.py`,
`harness/render-control-report.py`, and `harness/plot-load.py`, passing the final
review record with `--review`. The control renderer's `--output` is the Markdown
file `reports/03-gateway-api.md`; the other renderers take output directories.


### Recovering an interrupted qualification

Inspect the inactive unit and retain its output before rerunning. An interrupted
ClusterLoader2 process can leave its temporary `gwcmp-cl2-1` namespace even after
benchmark HTTPRoutes are removed. In this dedicated campaign cluster, capture
that namespace's JSON/UID, confirm it belongs to the stopped campaign, and delete
it explicitly before restarting the complete excluded phase. Do not enable broad
stale-namespace deletion or reuse a partial phase as an accepted repetition.
The CL2 configuration intentionally rejects pre-existing managed namespaces.


Reproduce the per-window isolation checks with `harness/audit-cpu-isolation.py`
against the eight-role analysis root and `harness/audit-kubernetes-startup.py`
against its `kclient` directory, supplying `kgateway/host-samples.jsonl` through
`--gateway-samples`. Each accepts `--phase pass1` (then pass2/pass3) and an explicit
`--output` path. They report facts/issues; they do not grant scientific approval.

Resource matrices are generated by `harness/render-resource-report.py`, using
`reports/data` plus the final CPU and Kubernetes host summaries through
`--cpu-hosts` and `--kubernetes-hosts`. Pass `--output reports` and the same
`--review` record. It requires all 606 gateway load windows and produces 202
three-pass resource groups; direct service has no gateway process.
