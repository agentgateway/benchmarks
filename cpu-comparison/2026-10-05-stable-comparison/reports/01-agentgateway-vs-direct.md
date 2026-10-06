# Agentgateway v1.6.0 versus direct service

This report compares the configured agentgateway path with the direct service path. The difference includes the extra network hop and configured gateway processing; it does not isolate intrinsic proxy CPU cost. The baseline is the same deterministic service on a separate VM; it does not include model inference. Results from older releases are not inputs to these averages.

Use the full matrices for every rate and payload: [common HTTP](matrices/common-http.md), [common AI transport](matrices/common-ai.md), [native AI](matrices/native-ai.md), [Kubernetes HTTP](matrices/kubernetes-http.md).

## Unlimited-rate Fortio cases

Ratios below are gateway successful throughput divided by direct throughput. Latency deltas are differences of three-run means; these are not per-request paired measurements. Unlimited-rate paths operate at different achieved rates, so these deltas do not isolate per-request proxy overhead. For fixed-rate comparisons, read delivered rate and errors beside latency.

| Profile | Case | Agentgateway successful RPS | Direct successful RPS | Fraction of direct | Mean latency delta ms |
| --- | --- | ---: | ---: | ---: | ---: |
| Standalone common forwarding | openai / 1024 B content, 32 connections, unlimited | 22,646 [22,423–22,998] | 58,129 [56,663–59,010] | 0.390 | 0.863 |
| Standalone common forwarding | openai / 16384 B content, 32 connections, unlimited | 10,207 [9,910–10,508] | 10,115 [9,971–10,387] | 1.009 | -0.028 |
| Standalone common forwarding | anthropic / 1024 B content, 32 connections, unlimited | 22,506 [21,949–23,208] | 59,954 [59,574–60,206] | 0.375 | 0.889 |
| Standalone common forwarding | anthropic / 16384 B content, 32 connections, unlimited | 10,414 [10,170–10,698] | 10,363 [10,175–10,624] | 1.005 | -0.015 |
| Standalone common forwarding | openai / 1024 B content, 512 connections, unlimited | 19,291 [18,758–19,701] | 70,302 [69,459–71,788] | 0.274 | 19.262 |
| Standalone common forwarding | openai / 16384 B content, 512 connections, unlimited | 11,654 [11,488–11,934] | 14,341 [14,183–14,532] | 0.813 | 8.248 |
| Standalone common forwarding | 0 B content, 1 connections, unlimited | 2,782 [2,596–2,910] | 5,830 [5,090–6,238] | 0.477 | 0.187 |
| Standalone common forwarding | 0 B content, 16 connections, unlimited | 23,817 [22,720–25,351] | 64,806 [62,457–66,667] | 0.368 | 0.426 |
| Standalone common forwarding | 0 B content, 512 connections, unlimited | 21,798 [21,205–22,135] | 127,635 [122,619–132,748] | 0.171 | 19.476 |
| Standalone common forwarding | 16384 B content, 1 connections, unlimited | 1,926 [1,832–2,053] | 3,550 [3,200–3,850] | 0.543 | 0.237 |
| Standalone common forwarding | 16384 B content, 16 connections, unlimited | 17,014 [16,437–18,126] | 36,269 [35,709–36,588] | 0.469 | 0.501 |
| Standalone common forwarding | 16384 B content, 512 connections, unlimited | 15,640 [15,263–15,837] | 56,319 [55,935–57,004] | 0.278 | 23.645 |
| Standalone native AI | openai / 1024 B content, 32 connections, unlimited | 14,041 [13,871–14,211] | 58,425 [57,827–58,983] | 0.240 | 1.732 |
| Standalone native AI | openai / 16384 B content, 32 connections, unlimited | 7,399 [7,321–7,488] | 10,031 [9,976–10,060] | 0.738 | 1.135 |
| Standalone native AI | anthropic / 1024 B content, 32 connections, unlimited | 14,158 [13,781–14,467] | 60,099 [59,160–60,756] | 0.236 | 1.729 |
| Standalone native AI | anthropic / 16384 B content, 32 connections, unlimited | 7,347 [7,214–7,438] | 10,267 [10,215–10,334] | 0.716 | 1.239 |
| Standalone native AI | translation / 1024 B content, 32 connections, unlimited | 12,822 [12,503–13,295] | 58,358 [57,366–59,208] | 0.220 | 1.949 |
| Standalone native AI | translation / 16384 B content, 32 connections, unlimited | 7,172 [7,116–7,226] | 10,081 [10,064–10,101] | 0.711 | 1.287 |
| Standalone native AI | openai / 1024 B content, 512 connections, unlimited | 12,205 [12,014–12,361] | 70,812 [69,812–71,367] | 0.172 | 34.709 |
| Standalone native AI | openai / 16384 B content, 512 connections, unlimited | 6,810 [6,718–6,872] | 14,377 [14,244–14,477] | 0.474 | 39.556 |
| Kubernetes HTTP | 0 B content, 1 connections, unlimited | 572.873 [551.251–606.071] | 5,656 [5,439–5,960] | 0.101 | 1.571 |
| Kubernetes HTTP | 0 B content, 16 connections, unlimited | 9,476 [9,177–9,654] | 61,518 [60,798–62,933] | 0.154 | 1.429 |
| Kubernetes HTTP | 0 B content, 512 connections, unlimited | 24,892 [24,689–25,159] | 112,367 [110,921–115,171] | 0.222 | 16.009 |
| Kubernetes HTTP | 16384 B content, 1 connections, unlimited | 534.786 [502.622–575.277] | 4,306 [4,028–4,595] | 0.124 | 1.643 |
| Kubernetes HTTP | 16384 B content, 16 connections, unlimited | 8,514 [8,344–8,644] | 34,838 [34,273–35,430] | 0.244 | 1.420 |
| Kubernetes HTTP | 16384 B content, 512 connections, unlimited | 16,196 [16,094–16,335] | 42,731 [41,917–43,183] | 0.379 | 19.623 |

## Reading the streaming results

The synthetic service emits 64 tokens after a nominal 25 ms initial delay, then 5 ms between tokens. AIPerf reports client-observed TTFT and ITL. These include service pacing, scheduling and network effects; they are not GPU inference performance. At fixed concurrency the backend pacing limits throughput, so small RPS differences need the latency ranges and errors beside them.

All full-matrix cells retain individual-run variation. Three runs on one placement provide descriptive repeatability, not a cloud-wide confidence interval. See [methodology and validity](05-methodology-and-validity.md).

Sampled CPU, cgroup memory and descriptor evidence is reported separately in [resource usage](08-resource-usage.md); those windows include startup and warmup.
