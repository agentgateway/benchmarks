#!/usr/bin/env python3
"""Bounded Fortio campaign. All trials, including failures, remain on disk."""
import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import time

from probe import CASES, endpoint, payload, probe

ROOT = Path(__file__).resolve().parent
FORTIO = "fortio/fortio@sha256:c26276816981710a38449d447d085737b7531d4aa0f8dd8aeffd4e709643370a"
TREATMENTS = ("direct", "agentgateway", "praxis")


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def output(cmd):
    return run(cmd, capture_output=True).stdout


def compose(*args):
    return ["docker", "compose", "-f", str(ROOT / "compose.yaml"), *args]


def schedule(args):
    rows = []
    rng = random.Random(args.seed)
    # Each treatment appears once in each position over three repeats.
    for case, size, qps in itertools.product(args.cases, args.sizes, args.qps):
        order = list(TREATMENTS)
        rng.shuffle(order)
        for repeat in range(args.repetitions):
            for pos in range(3):
                rows.append({"case":case,"size":size,"qps":qps,"repeat":repeat+1,"position":pos+1,"gateway":order[(pos+repeat)%3]})
    return rows


def fortio_command(row, directory, duration, connections, warmup=False):
    gateway, case = row["gateway"], row["case"]
    payload_case = "openai" if gateway == "direct" and case == "translation" else case
    (directory / "request.json").write_bytes(payload(payload_case,row["size"]))
    name = "warmup" if warmup else "fortio"
    client_name = "agw-praxis-client-" + hashlib.sha256(str(directory).encode()).hexdigest()[:12] + "-" + name
    return ["docker","run","--rm","--name",client_name,"--user",f"{os.getuid()}:{os.getgid()}","--network","agw-praxis-ai-bench_default","--cpuset-cpus",os.environ.get("CLIENT_CPUSET","6-7"),"--cpus","2","--memory","2g","-v",f"{directory}:/results",FORTIO,"load","-qps",str(row["qps"]),"-t",str(duration)+"s","-c",str(connections),"-uniform","-nocatchup","-timeout","10s","-X","POST","-payload-file","/results/request.json","-H","Content-Type: application/json","-H","Authorization: Bearer dummy","-H","x-api-key: dummy","-H","anthropic-version: 2023-06-01","-H",f"x-bench-output-bytes: {row['size']}","-json",f"/results/{name}.json","-r","0.000001",endpoint(gateway,case,container=True)]


def cpu_set(value):
    if not re.fullmatch(r"\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*", value):
        raise ValueError(f"Invalid CPU set: {value}")
    result = set()
    for part in value.split(","):
        bounds = [int(v) for v in part.split("-")]
        if bounds[0] > bounds[-1]:
            raise ValueError(f"Reversed CPU range: {part}")
        result.update(range(bounds[0], bounds[-1] + 1))
    return result


def run_phase(row, trial, duration, connections, warmup):
    name = "warmup" if warmup else "fortio"
    cmd = fortio_command(row, trial, duration, connections, warmup)
    client_name = cmd[cmd.index("--name") + 1]
    (trial / ("warmup-command.json" if warmup else "command.json")).write_text(json.dumps(cmd, indent=2))
    started = time.monotonic()
    phase = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    stats = client = None
    with (trial / ("warmup-stats.jsonl" if warmup else "stats.jsonl")).open("w") as stats_file:
        try:
            with (trial / f"{name}.log").open("w") as log:
                client = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)
                # Wait briefly for Docker to create the named client, then sample
                # only this trial's services. Never collect unrelated containers.
                for _ in range(30):
                    if client.poll() is not None:
                        break
                    ready = subprocess.run(["docker", "inspect", client_name],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                           timeout=5)
                    if ready.returncode == 0:
                        break
                    time.sleep(0.1)
                names = ["agw-praxis-ai-bench-mock-1", client_name]
                if row["gateway"] != "direct":
                    names.append(f"agw-praxis-ai-bench-{row['gateway']}-1")
                stats = subprocess.Popen(["docker", "stats", "--format", "{{json .}}", *names],
                                         stdout=stats_file, stderr=subprocess.STDOUT, text=True)
                code = client.wait(timeout=duration + 60)
                phase["exit_code"] = code
                if code:
                    raise RuntimeError(f"Fortio failed ({code}); see {trial}")
        finally:
            # Killing the docker CLI alone does not reliably kill its container.
            try:
                subprocess.run(["docker", "rm", "-f", client_name], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=15)
            except (OSError, subprocess.TimeoutExpired) as exc:
                phase["cleanup_error"] = str(exc)
            if client is not None and client.poll() is None:
                client.kill()
                client.wait(timeout=10)
            if stats is not None:
                stats.terminate()
                try:
                    stats.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    stats.kill()
                    stats.wait(timeout=10)
            phase["elapsed_seconds"] = time.monotonic() - started
            (trial / f"{name}-phase.json").write_text(json.dumps(phase, indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"results"/time.strftime("%Y%m%dT%H%M%SZ",time.gmtime()))
    p.add_argument("--cases",nargs="+",choices=list(CASES),default=list(CASES))
    p.add_argument("--sizes",nargs="+",type=int,default=[1024,16384])
    p.add_argument("--qps",nargs="+",type=int,default=[1000,3000,0])
    p.add_argument("--duration",type=int,default=30)
    p.add_argument("--warmup",type=int,default=5)
    p.add_argument("--repetitions",type=int,default=6)
    p.add_argument("--connections",type=int,default=32)
    p.add_argument("--seed",type=int,default=20261001)
    p.add_argument("--initial",action="store_true",help="One preliminary performance round; cannot establish variance or statistical superiority")
    p.add_argument("--smoke",action="store_true",help="Qualification only; results not publishable for performance claims")
    p.add_argument("--dry-run",action="store_true")
    args=p.parse_args()
    if args.initial and args.smoke:
        p.error("Select --initial or --smoke, not both")
    if args.initial:
        args.repetitions=1
    if args.smoke:
        args.duration,args.warmup,args.repetitions,args.qps,args.sizes=2,1,1,[10],[1024]
    if min(args.duration,args.warmup,args.repetitions,args.connections,*args.sizes)<=0 or min(args.qps)<0:
        p.error("Durations, repetitions, connections and sizes must be positive; QPS must be nonnegative")
    if max(args.sizes) > 65536:
        p.error("Sizes must be <=65536: the deterministic backend caps output at 64 KiB")
    if not args.smoke and (args.duration<30 or (args.repetitions<5 and not args.initial)):
        p.error("Performance campaigns require >=30 seconds and >=5 repetitions; use --initial for one preliminary round or --smoke for qualification")
    rows=schedule(args)
    args.output=args.output.resolve()
    if args.dry_run:
        print(json.dumps({"trials":rows,"minimum_load_seconds":len(rows)*(args.duration+args.warmup),"mode":"smoke" if args.smoke else "preliminary-performance" if args.initial else "performance"},indent=2));return
    info=json.loads(output(["docker","info","--format","{{json .}} "]))
    if not args.smoke and (info["Architecture"] not in ("x86_64","amd64") or info["NCPU"]<8):
        p.error("Comparative performance requires native x86 Docker host with >=8 CPUs; local emulation is qualification-only")
    cpu_values = {name: os.environ.get(name, default) for name, default in
                  (("GATEWAY_CPUSET", "2-3"), ("MOCK_CPUSET", "4-5"), ("CLIENT_CPUSET", "6-7"))}
    try:
        selected_cpus = {name: cpu_set(value) for name, value in cpu_values.items()}
    except ValueError as exc:
        p.error(str(exc))
    if any(max(value) >= info["NCPU"] for value in selected_cpus.values()):
        p.error("A selected CPU is outside the Docker host's available CPU range")
    if not args.smoke:
        if any(len(value) != 2 for value in selected_cpus.values()):
            p.error("Performance requires exactly two logical CPUs per gateway, mock and client CPU set")
        if any(a & b for a, b in itertools.combinations(selected_cpus.values(), 2)):
            p.error("Performance CPU sets must not overlap")
    if output(compose("ps", "--all", "--quiet")).strip():
        p.error("The fixed benchmark Compose project already has containers; inspect and stop it before a new campaign")
    if args.output.exists():
        p.error("Refusing to overwrite an existing campaign")
    args.output.mkdir(parents=True)
    manifest={"started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"mode":"qualification-only" if args.smoke else "preliminary-performance" if args.initial else "performance","parameters":vars(args)|{"output":str(args.output)},"cpu_sets":cpu_values,"host":{"platform":platform.platform(),"docker_arch":info["Architecture"],"docker_cpus":info["NCPU"],"docker_memory":info["MemTotal"],"docker_version":info["ServerVersion"]},"fortio_image":FORTIO,"trials":rows,"files_sha256":{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in ROOT.rglob("*") if f.is_file() and (f.suffix in (".py",".yaml",".go",".sh") or f.name == "Dockerfile") and "results" not in f.parts and "__pycache__" not in f.parts}}
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2))
    summary=[]
    status={"status":"incomplete", "completed_trials":0, "planned_trials":len(rows)}
    active_trial=None
    try:
        # Rebuild from the recorded fixture source for the Docker host architecture;
        # a pre-existing binary could otherwise be stale or for the wrong platform.
        run(["bash", str(ROOT / "build-mock.sh")], timeout=120)
        manifest["mock_binary_sha256"] = hashlib.sha256((ROOT / "mock/mock-server").read_bytes()).hexdigest()
        (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2))
        run(compose("up","-d","--build"), timeout=600)
        # Readiness uses protocol requests. Startup failures retain logs in finally.
        for gateway in TREATMENTS:
            for attempt in range(30):
                try: probe(gateway,"openai");break
                except Exception:
                    if attempt==29: raise
                    time.sleep(1)
        with (args.output/"qualification.jsonl").open("w") as stream:
            for gateway,case,size,mode in itertools.product(TREATMENTS,args.cases,args.sizes,((False,False),(True,False),(False,True))):
                try:
                    result=probe(gateway,case,*mode,size=size)
                except Exception as exc:
                    result={"gateway":gateway,"case":case,"stream":mode[0],"upstream_error":mode[1],"requested_bytes":size,"passed":False,"error":repr(exc)}
                    stream.write(json.dumps(result)+"\n");stream.flush()
                    raise
                stream.write(json.dumps(result)+"\n");stream.flush()
        (args.output/"compose-resolved.yaml").write_text(output(compose("config")))
        ids=output(compose("ps","-q")).split()
        (args.output/"container-inspect.json").write_text(output(["docker","inspect",*ids]))
        run(["docker","pull",FORTIO], timeout=300)
        service_images = json.loads(output(compose("config", "--format", "json")))
        image_refs = [service["image"] for service in service_images["services"].values()] + [FORTIO]
        images = json.loads(output(["docker", "image", "inspect", *image_refs]))
        (args.output/"image-inspect.json").write_text(json.dumps(images,indent=2))
        if not args.smoke and any(image["Architecture"] != "amd64" for image in images):
            raise RuntimeError("All performance images must be native amd64; image inspection found a mismatch")
        for index,row in enumerate(rows,1):
            trial=args.output/f"{index:03d}-{row['gateway']}-{row['case']}-{row['size']}-q{row['qps']}-r{row['repeat']}"
            trial.mkdir()
            active_trial = row | {"trial":str(trial.relative_to(args.output))}
            # Same CPU set is used sequentially. Stop idle gateways to eliminate background contention.
            for gateway in ("agentgateway","praxis"):
                run(compose("start" if gateway==row["gateway"] else "stop",gateway),stdout=subprocess.DEVNULL)
            if row["gateway"]!="direct":
                for attempt in range(30):
                    try: probe(row["gateway"],row["case"]);break
                    except Exception:
                        if attempt==29: raise
                        time.sleep(1)
            print(f"Trial {index}/{len(rows)}: {row}",flush=True)
            for warmup,duration in ((True,args.warmup),(False,args.duration)):
                run_phase(row,trial,duration,args.connections,warmup)
            value=json.loads((trial/"fortio.json").read_text())
            n=sum(value["RetCodes"].values());ok=value["RetCodes"].get("200",0)
            duration=value["ActualDuration"]/1e9
            if duration <= 0 or n <= 0:
                raise RuntimeError(f"Fortio produced no valid measurement interval or requests: {trial}")
            record=row|{"trial":str(trial.relative_to(args.output)),"requests":n,"successes":ok,"errors":n-ok,"actual_qps":value["ActualQPS"],"successful_qps":ok/duration,"error_fraction":(n-ok)/n if n else 1,"actual_seconds":duration}
            for percentile in value["DurationHistogram"]["Percentiles"]:
                record[f"p{percentile['Percentile']:g}_ms"]=percentile["Value"]*1000
            record["target_met"]=record["error_fraction"]<=0.001 and (row["qps"]==0 or record["successful_qps"]>=row["qps"]*0.99)
            summary.append(record)
            status["completed_trials"] = len(summary)
            (args.output/"summary.json").write_text(json.dumps(summary,indent=2))
        with (args.output/"summary.csv").open("w",newline="") as out:
            writer=csv.DictWriter(out,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
        status["status"] = "complete"
        status["all_targets_met"] = all(record["target_met"] for record in summary)
    except BaseException as exc:
        status["error"] = repr(exc)
        status["failed_trial"] = active_trial
        raise
    finally:
        with (args.output/"containers.log").open("w") as log:
            try:
                subprocess.run(compose("logs","--no-color"),stdout=log,stderr=subprocess.STDOUT,text=True,timeout=30)
                stopped = subprocess.run(compose("down"),stdout=log,stderr=subprocess.STDOUT,text=True,timeout=60)
                status["cleanup_exit_code"] = stopped.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                status["cleanup_error"] = repr(exc)
        (args.output/"campaign-status.json").write_text(json.dumps(status,indent=2))
        hashes={str(f.relative_to(args.output)):hashlib.sha256(f.read_bytes()).hexdigest() for f in args.output.rglob("*") if f.is_file()}
        (args.output/"SHA256SUMS.json").write_text(json.dumps(hashes,indent=2))


if __name__=="__main__":
    main()
