# Reproduce the extended Gateway API comparison

Use a disposable GCP project or isolated VMs in a project where you may create and
delete compute instances. Commands here incur CPU VM charges; no GPUs are used.
Replace project/zone/prefix consistently if adapting this campaign. Never delete
instances based only on a familiar-looking name: teardown verifies captured IDs.

## Build and pin

1. Check out this repository revision and enter this campaign directory.
2. Check out kubernetes-sigs/gateway-api at
   `e7677b70ae75d14a4448fba94870e7deea6cf0ad`. From its `conformance` module, run
   `CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go test -c -o /path/to/campaign/.work/gateway-conformance.test`.
   The original binary used Go 1.26.4. Record the rebuilt binary SHA-256 and compare
   source/compiler identity with selection.json; absolute build paths can make a
   rebuilt binary hash differ. Verify any reused original binary against its recorded SHA-256.
3. Generate the catalog by running `go run /path/to/campaign/harness/catalog.go`
   from that same module. Standard output is JSON; standard error ends with the
   comma-separated feature selector. The checked-in catalog and configs/features.txt
   are the exact selection used here. If regenerating the JSON, run
   `python3 harness/annotate-catalog.py /path/to/gateway-api evidence/test-catalog.json`
   from this campaign directory to add pinned source links; this does not change
   selected tests or feature flags.
4. Check out praxis-proxy/operator at
   `fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c`, archive the repository contents into
   `.work/praxis-operator-source.tar.gz`, preserving its Containerfile and Cargo.lock.
   Do not follow moving branch or image tags during a repetition campaign.
5. The bootstrap currently reuses the prior campaign's mock-server and clusterloader2
   binaries in `.work`. Clusterloader2 is transferred but is not invoked in this
   campaign. The mock backend is an auxiliary fixture; upstream conformance uses its
   own echo fixtures. Build instructions for those inherited artifacts are in the
   [shared fixture build instructions](../../2026-10-05-stable-comparison/docs/REPRODUCE.md#exact-tool-builds). No load-generator scores enter
   this report. Keep this campaign’s conformance v1.5.1 source pin when following those shared mock/ClusterLoader2 build steps; the later campaign’s corrected conformance binary is a different input.

## Provision and qualify

Run `bash infra/create-kubernetes-vm.sh ROLE` for each of kcontrol, kcontroller,
kgateway, kbackend and kclient. Keep each `.work/create-ROLE.json`; it records resource
identity and the twelve-hour auto-delete setting. Run `python3 infra/provision-kubernetes.py`.

The VM bootstrap masks automatic apt maintenance before measurements. Verify
`apt-daily.timer` and `apt-daily-upgrade.timer` are masked and no package upgrade is
active; `infra/freeze-maintenance.sh` provides the same check for existing disposable
hosts. This prevents package-triggered restarts of supervised benchmark jobs.

The client bootstrap applies `infra/configure-tcp-client.sh`. Verify
`net.ipv4.tcp_syn_retries=2` and `net.ipv4.tcp_syn_linear_timeouts=4` before any measured
run; retain the before/after record. See [why this is needed](infrastructure-investigation.md).

Verify all nodes are Ready, chart installations complete, container digests match
selection.json, and both API controller Deployments are available. Ensure the latest
harness scripts have been copied to `/opt/gateway-benchmark` on kclient. The runner
uses `/etc/rancher/k3s/benchmark.kubeconfig`; never publish that credential.

On kclient, run as root from `/opt/gateway-benchmark`:

```sh
bash run-one.sh praxis-v0.5.2 qualification agentgateway smoke
bash run-one.sh praxis-v0.5.2 qualification praxis smoke
bash run-one.sh praxis-nightly-20261002 qualification praxis smoke
```

Qualification records are separate from measured repetitions. Investigate setup
failures before attempting the full campaign; do not silently patch products.

Qualify static allocation with `harness/qualify-static-address.sh` on kclient while
no suite is running. It temporarily assigns the reserved VIP to the direct fixture,
verifies reachability and deletes that Service. Never run this while the suite may
need the same reserved address.

## Three repetitions

For each campaign (`praxis-v0.5.2`, `praxis-nightly-20261002`), execute:

```sh
python3 infra/run-case.py CAMPAIGN pass1 agentgateway
# Wait for JOB-FINISHED and review before dispatching the next case.
python3 infra/run-case.py CAMPAIGN pass1 praxis
# Review the complete first pair and record its validity before proceeding.
python3 infra/run-case.py CAMPAIGN pass2 praxis
python3 infra/run-case.py CAMPAIGN pass2 agentgateway
python3 infra/run-case.py CAMPAIGN pass3 agentgateway
python3 infra/run-case.py CAMPAIGN pass3 praxis
```

These commands dispatch supervised systemd jobs from the local host. Wait for each
case to finish before issuing the next command; do not paste this block as a queue.
Before pass two, write `evidence/validity/CAMPAIGN-pass1.json` with
`"infrastructure_valid": true` only after the review supports that conclusion.
Retain the checks and explanation in the same record. `harness/review-runtime.py`
summarizes collected state, but does not automatically approve a run.
It refuses to start while another campaign job is running and applies a 1,048,576
open-file limit to measured runs. `run-one.sh`
refuses to overwrite an existing result directory, selects exactly one active
controller and writes product/assertion exit codes independently of cleanup status.
A finished job is not by itself a passing or infrastructure-valid test.

`run-conformance.sh` contains the complete upstream flags. Per-test limits remain
upstream defaults. Runtime monitoring captures non-secret Kubernetes state every
30 seconds; host monitoring samples every 15 seconds. Save controller output as
well as upstream report.yaml and full.log. During the third Praxis release run,
`harness/capture-operator-restarts.py CASE_DIRECTORY` was additionally polled every
50 seconds to preserve previous-container logs when existing runtime snapshots
showed a restart. Earlier runs used manual capture. This read-only diagnostic does
not change test assertions or product configuration. For a nightly attempt, run `harness/capture-nightly-setup.py CASE_DIRECTORY` on
kclient once the four base Deployments and ConfigMaps exist and before setup exits.
It captures generated configuration and logs without changing resources; sanitize
its fixture private keys before Git publication.
The upstream profile reports can omit
tests whose feature combination is not assigned to a profile; use the supplied
catalog and top-level log parser to account for all 107 selected cases.

## Export, report, and delete

Run `infra/export-kubernetes-evidence.sh` with no tests active. It exports host
archives and sanitizes known credential-bearing evidence. Review sanitization,
calculate checksums and verify the uploaded private release assets against local
sizes and digests. Restore raw results from kclient's archive to `results/` and run
`python3 harness/summarize.py .`, `python3 harness/aggregate.py`, and
`python3 harness/write-matrix.py`, and `python3 harness/extract-assertions.py`; retain qualification and invalid attempts separately.
Use `harness/import-results.py` when importing an unsanitized local snapshot so
generated fixture private keys are removed before Git publication.

Run `python3 harness/check-evidence.py` to check archive integrity and known
credential patterns, then `python3 harness/review-hosts.py` after archive export and record the human
host-health decision in `evidence/validity/host-runtime-decision.json`. With every
individual run reviewed, `python3 harness/final-audit.py` verifies the twelve
measured attempts and writes the final validation inventory.

After final validity review, `python3 infra/publish-evidence.py` creates the private
release and verifies each remote asset size and SHA-256 digest. It refuses to
overwrite an existing release; inspect and verify an existing release if a prior
upload was interrupted. Then run `python3 infra/teardown.py`. It checks each VM's
ID, campaign label and boot-disk auto-delete setting before deleting only those
resources. It inventories the project and removes temporary local cluster credentials.
Keep the cleanup verification and estimated cost report with the results.
