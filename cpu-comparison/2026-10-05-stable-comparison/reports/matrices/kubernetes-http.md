# Kubernetes HTTP: HTTP matrix

Values are arithmetic means of three runs followed by [minimum–maximum].
Latency p99 is the mean of each run's p99, **not a pooled p99**. RPS counts successful
responses. Fortio latency includes all response statuses. Do not compare different
workloads, traffic rates, APIs or deployment profiles as if they were equal work.
Every individual pass and raw artifact path is in [load-rows.json](../data/load-rows.json).

The pinned operator/core nightly pairing could not start; it is **not evaluated**, not zero throughput.

## fortio

| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |
| --- | --- | ---: | ---: | ---: | --- |
| 0 B content, 1 connections, unlimited | Direct service | 5,656 [5,439–5,960] | 0.177 [0.167–0.183] | 0.284 [0.255–0.303] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, unlimited | Agentgateway v1.6.0 | 572.873 [551.251–606.071] | 1.748 [1.649–1.813] | 1.998 [1.996–1.999] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, unlimited | Praxis core v0.5.2 | 605.950 [571.020–639.645] | 1.653 [1.563–1.750] | 1.996 [1.995–1.997] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Direct service | 750.354 [735.627–767.438] | 0.258 [0.230–0.281] | 0.372 [0.336–0.396] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 348.422 [337.340–355.219] | 1.794 [1.741–1.880] | 2.192 [1.997–2.580] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Praxis core v0.5.2 | 358.864 [337.433–372.473] | 1.714 [1.611–1.875] | 2.158 [1.996–2.483] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Direct service | 61,518 [60,798–62,933] | 0.260 [0.254–0.263] | 1.230 [1.190–1.252] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Agentgateway v1.6.0 | 9,476 [9,177–9,654] | 1.689 [1.657–1.743] | 2.041 [1.997–2.130] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Praxis core v0.5.2 | 9,734 [9,294–10,016] | 1.645 [1.597–1.721] | 1.997 [1.995–1.999] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Direct service | 999.469 [999.462–999.477] | 0.271 [0.247–0.292] | 0.384 [0.347–0.410] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.418 [999.412–999.424] | 1.710 [1.663–1.798] | 1.997 [1.996–2.000] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 999.428 [999.416–999.438] | 1.733 [1.669–1.822] | 2.106 [1.995–2.328] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Direct service | 112,367 [110,921–115,171] | 4.556 [4.444–4.614] | 24.359 [23.554–25.171] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 24,892 [24,689–25,159] | 20.565 [20.345–20.732] | 37.407 [36.976–37.729] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Praxis core v0.5.2 | 32,008 [31,969–32,077] | 15.991 [15.957–16.010] | 39.403 [39.360–39.430] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Direct service | 983.062 [983.053–983.066] | 0.284 [0.254–0.314] | 0.444 [0.347–0.570] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 983.004 [982.995–983.019] | 1.771 [1.726–1.819] | 2.002 [1.997–2.010] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Praxis core v0.5.2 | 982.996 [982.988–983.005] | 1.728 [1.683–1.815] | 2.217 [1.996–2.659] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Direct service | 4,306 [4,028–4,595] | 0.232 [0.217–0.248] | 0.422 [0.400–0.438] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Agentgateway v1.6.0 | 534.786 [502.622–575.277] | 1.875 [1.738–1.989] | 2.599 [1.998–2.973] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Praxis core v0.5.2 | 548.411 [535.891–572.182] | 1.825 [1.747–1.865] | 2.465 [2.000–2.703] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Direct service | 709.974 [696.037–728.991] | 0.331 [0.298–0.352] | 0.521 [0.466–0.553] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 327.077 [319.532–333.500] | 1.977 [1.919–2.054] | 2.933 [2.861–2.988] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Praxis core v0.5.2 | 340.929 [338.154–342.760] | 1.852 [1.840–1.865] | 2.672 [2.632–2.731] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Direct service | 34,838 [34,273–35,430] | 0.459 [0.451–0.466] | 1.844 [1.835–1.854] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Agentgateway v1.6.0 | 8,514 [8,344–8,644] | 1.879 [1.851–1.917] | 2.943 [2.927–2.961] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Praxis core v0.5.2 | 8,688 [8,671–8,699] | 1.841 [1.839–1.845] | 2.917 [2.916–2.918] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Direct service | 999.474 [999.470–999.479] | 0.340 [0.306–0.368] | 0.568 [0.525–0.592] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.419 [999.402–999.435] | 1.883 [1.824–1.939] | 2.853 [2.688–2.953] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 999.421 [999.404–999.434] | 1.821 [1.790–1.852] | 2.659 [2.444–2.827] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Direct service | 42,731 [41,917–43,183] | 11.980 [11.852–12.210] | 56.413 [53.257–59.061] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 16,196 [16,094–16,335] | 31.603 [31.331–31.802] | 49.544 [49.415–49.748] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Praxis core v0.5.2 | 18,357 [18,284–18,432] | 27.878 [27.767–27.989] | 49.299 [49.196–49.369] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Direct service | 983.051 [983.032–983.061] | 0.411 [0.377–0.434] | 0.577 [0.526–0.606] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 982.985 [982.979–982.991] | 2.567 [2.514–2.659] | 2.994 [2.993–2.996] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Praxis core v0.5.2 | 982.992 [982.984–982.997] | 2.528 [2.493–2.554] | 2.992 [2.991–2.993] | 0.000 [0.000–0.000] errors/run |

## nighthawk

| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |
| --- | --- | ---: | ---: | ---: | --- |
| 0 B content, 16 connections, 1000 RPS | Direct service | 1,000 [1000.000–1,000] | 0.191 [0.166–0.205] | 0.275 [0.238–0.300] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 0 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.899 [999.899–999.899] | 1.631 [1.579–1.681] | 1.838 [1.810–1.881] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 1.667 [1.000–2.000] |
| 0 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 999.899 [999.899–999.900] | 1.657 [1.624–1.676] | 1.846 [1.811–1.865] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 2.000 [2.000–2.000] |
| 16384 B content, 16 connections, 1000 RPS | Direct service | 1,000 [1000.000–1,000] | 0.246 [0.230–0.255] | 0.382 [0.352–0.404] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 16384 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.900 [999.899–999.900] | 1.693 [1.640–1.783] | 1.937 [1.894–2.016] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 2.000 [2.000–2.000] |
| 16384 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 999.899 [999.899–999.900] | 1.742 [1.706–1.791] | 1.995 [1.973–2.022] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 2.000 [2.000–2.000] |

† Nighthawk reports the nearest quantile at or above p99; the exact percentile is retained per run. In-flight requests at cutoff are distinct from confirmed failures.
