#!/bin/bash
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
cd /opt/gateway-benchmark
wait_empty() {
 local kind="$1" namespace="$2" count
 for i in $(seq 1 180); do
  count=$(kubectl get "$kind" -n "$namespace" -o json | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["items"]))')
  [ "$count" = 0 ] && return 0
  sleep 1
 done
 return 1
}
requested="$1"
case "$requested" in
 praxis-release) treatment=praxis; image=ghcr.io/praxis-proxy/praxis@sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8;;
 praxis-nightly) treatment=praxis; image=ghcr.io/praxis-proxy/praxis@sha256:be62d256d5ec92aacb1216baba506aac763e2100f9eb361820a5c27c54e17be8;;
 agentgateway) treatment="$requested"; image=ghcr.io/agentgateway/agentgateway@sha256:9d3e6044ddcdc0878b1787f77bd401252b95e22684203fb5e874c4c42d2ed90c;;
 direct) treatment="$requested";;
 *) exit 2;;
esac
case "$treatment" in direct|agentgateway|praxis) ;; *) exit 2 ;; esac
bash /opt/gateway-benchmark/cleanup-scale-routes.sh
kubectl delete gateway benchmark -n gateway-benchmark --ignore-not-found --timeout=180s
kubectl delete httproute benchmark -n gateway-benchmark --ignore-not-found --timeout=180s
# Wait for owned data-plane pods to disappear before stopping its controller.
for i in $(seq 1 60); do
 count=$(kubectl get pods -n gateway-benchmark -o json | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["items"]))')
 [ "$count" = 0 ] && break
 sleep 2
done
[ "$count" = 0 ]
wait_empty services gateway-benchmark
# A rolling controller update can retain an old leader after rollout status
# succeeds. Stop both controllers before changing the next treatment's image.
kubectl scale deployment agentgateway -n agentgateway-system --replicas=0
wait_empty pods agentgateway-system
kubectl scale deployment praxis-operator -n praxis-system --replicas=0
wait_empty pods praxis-system
wait_empty deployments gateway-benchmark
if [ "$treatment" = direct ]; then
 kubectl scale deployment agentgateway -n agentgateway-system --replicas=0
 wait_empty pods agentgateway-system
 kubectl scale deployment praxis-operator -n praxis-system --replicas=0
 wait_empty pods praxis-system
 printf '{"treatment":"direct","url":"http://10.128.15.236:30081"}\n' | python3 /opt/gateway-benchmark/wait-endpoint.py
 exit 0
fi
if [ "$treatment" = agentgateway ]; then
 kubectl scale deployment praxis-operator -n praxis-system --replicas=0
 wait_empty pods praxis-system
 kubectl scale deployment agentgateway -n agentgateway-system --replicas=2
 kubectl rollout status deployment/agentgateway -n agentgateway-system --timeout=180s
else
 kubectl scale deployment agentgateway -n agentgateway-system --replicas=0
 wait_empty pods agentgateway-system
 kubectl set env deployment/praxis-operator -n praxis-system PRAXIS_IMAGE="$image"
 kubectl scale deployment praxis-operator -n praxis-system --replicas=2
 kubectl rollout status deployment/praxis-operator -n praxis-system --timeout=180s
fi
sed "s/REPLACE_GATEWAY_CLASS/$treatment/" configs/kubernetes/gateway.yaml | kubectl apply -f -
kubectl wait gateway/benchmark -n gateway-benchmark --for=condition=Programmed --timeout=300s
kubectl wait pod -n gateway-benchmark --all --for=condition=Ready --timeout=180s
python3 /opt/gateway-benchmark/wait-single-gateway.py --expected-image "$image"
kubectl get svc -n gateway-benchmark -o json | python3 -c 'import json,sys;v=json.load(sys.stdin)["items"];assert len(v)==1;v=v[0];p=next(p for p in v["spec"]["ports"] if p["port"]==80);print(json.dumps({"service":v["metadata"]["name"],"url":"http://10.128.15.214:"+str(p["nodePort"]),"load_balancer":v["status"].get("loadBalancer")}))' | python3 /opt/gateway-benchmark/wait-endpoint.py
