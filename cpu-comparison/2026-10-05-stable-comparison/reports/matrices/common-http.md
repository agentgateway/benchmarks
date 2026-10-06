# Standalone common forwarding: HTTP matrix

Values are arithmetic means of three runs followed by [minimum–maximum].
Latency p99 is the mean of each run's p99, **not a pooled p99**. RPS counts successful
responses. Fortio latency includes all response statuses. Do not compare different
workloads, traffic rates, APIs or deployment profiles as if they were equal work.
Every individual pass and raw artifact path is in [load-rows.json](../data/load-rows.json).

## fortio

| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |
| --- | --- | ---: | ---: | ---: | --- |
| 0 B content, 1 connections, unlimited | Direct service | 5,830 [5,090–6,238] | 0.172 [0.160–0.196] | 0.303 [0.250–0.397] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, unlimited | Agentgateway v1.6.0 | 2,782 [2,596–2,910] | 0.360 [0.343–0.385] | 0.559 [0.550–0.571] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, unlimited | Praxis core v0.5.2 | 3,334 [3,122–3,484] | 0.300 [0.286–0.320] | 0.459 [0.437–0.493] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, unlimited | Praxis core nightly-20261002 | 2,963 [2,774–3,145] | 0.338 [0.317–0.360] | 0.519 [0.482–0.587] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Direct service | 743.737 [733.326–751.248] | 0.261 [0.250–0.276] | 0.386 [0.349–0.448] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 635.018 [621.425–661.119] | 0.497 [0.437–0.531] | 0.680 [0.598–0.745] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Praxis core v0.5.2 | 669.400 [657.198–687.575] | 0.417 [0.380–0.443] | 0.607 [0.558–0.668] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 1 connections, 1000 RPS | Praxis core nightly-20261002 | 640.952 [633.151–648.701] | 0.481 [0.462–0.499] | 0.687 [0.667–0.716] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Direct service | 64,806 [62,457–66,667] | 0.246 [0.239–0.256] | 1.227 [1.196–1.263] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Agentgateway v1.6.0 | 23,817 [22,720–25,351] | 0.673 [0.631–0.704] | 1.559 [1.456–1.619] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Praxis core v0.5.2 | 37,779 [36,728–39,142] | 0.423 [0.408–0.435] | 1.294 [1.247–1.344] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, unlimited | Praxis core nightly-20261002 | 27,490 [27,252–27,663] | 0.581 [0.578–0.587] | 1.452 [1.440–1.462] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Direct service | 999.466 [999.461–999.475] | 0.281 [0.268–0.300] | 0.425 [0.385–0.493] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.465 [999.459–999.474] | 0.495 [0.466–0.516] | 0.714 [0.669–0.778] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 999.475 [999.463–999.484] | 0.443 [0.417–0.470] | 0.637 [0.596–0.691] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 999.464 [999.456–999.476] | 0.485 [0.467–0.503] | 0.699 [0.664–0.742] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Direct service | 127,635 [122,619–132,748] | 4.014 [3.855–4.174] | 18.843 [18.533–19.016] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 21,798 [21,205–22,135] | 23.490 [23.122–24.139] | 40.722 [39.295–42.960] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Praxis core v0.5.2 | 33,682 [32,123–34,563] | 15.212 [14.807–15.933] | 40.878 [39.871–42.370] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 22,832 [22,356–23,113] | 22.422 [22.144–22.894] | 48.175 [47.198–49.117] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Direct service | 983.057 [983.036–983.068] | 0.287 [0.282–0.295] | 0.417 [0.394–0.463] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 983.051 [983.029–983.062] | 0.483 [0.455–0.502] | 0.689 [0.629–0.748] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Praxis core v0.5.2 | 983.050 [983.044–983.061] | 0.441 [0.419–0.469] | 0.628 [0.593–0.692] | 0.000 [0.000–0.000] errors/run |
| 0 B content, 512 connections, 1000 RPS | Praxis core nightly-20261002 | 983.057 [983.051–983.061] | 0.490 [0.474–0.504] | 0.706 [0.677–0.747] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Direct service | 3,550 [3,200–3,850] | 0.283 [0.259–0.312] | 0.492 [0.430–0.603] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Agentgateway v1.6.0 | 1,926 [1,832–2,053] | 0.520 [0.487–0.545] | 0.760 [0.681–0.859] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Praxis core v0.5.2 | 2,090 [2,051–2,122] | 0.478 [0.471–0.487] | 1.401 [0.988–1.664] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, unlimited | Praxis core nightly-20261002 | 1,988 [1,915–2,047] | 0.503 [0.488–0.521] | 1.370 [0.911–1.635] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Direct service | 707.867 [693.249–718.354] | 0.330 [0.311–0.356] | 0.555 [0.511–0.622] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 591.902 [581.141–607.829] | 0.610 [0.569–0.639] | 0.851 [0.781–0.940] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Praxis core v0.5.2 | 617.087 [605.406–625.690] | 0.543 [0.522–0.574] | 0.816 [0.779–0.888] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 1 connections, 1000 RPS | Praxis core nightly-20261002 | 593.132 [586.984–599.479] | 0.606 [0.589–0.625] | 0.879 [0.833–0.939] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Direct service | 36,269 [35,709–36,588] | 0.441 [0.437–0.447] | 1.776 [1.763–1.786] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Agentgateway v1.6.0 | 17,014 [16,437–18,126] | 0.942 [0.882–0.973] | 1.971 [1.958–1.977] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Praxis core v0.5.2 | 21,336 [19,856–22,132] | 0.751 [0.722–0.805] | 1.882 [1.855–1.920] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, unlimited | Praxis core nightly-20261002 | 16,604 [16,529–16,684] | 0.963 [0.958–0.967] | 1.977 [1.977–1.977] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Direct service | 999.468 [999.457–999.474] | 0.355 [0.329–0.380] | 0.607 [0.556–0.674] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.456 [999.447–999.473] | 0.610 [0.576–0.642] | 0.875 [0.799–0.962] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 999.458 [999.442–999.478] | 0.542 [0.525–0.573] | 0.825 [0.788–0.891] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 999.448 [999.444–999.453] | 0.590 [0.590–0.591] | 0.869 [0.850–0.896] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Direct service | 56,319 [55,935–57,004] | 9.087 [8.978–9.146] | 36.132 [35.800–36.443] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 15,640 [15,263–15,837] | 32.732 [32.315–33.531] | 53.187 [49.538–60.447] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Praxis core v0.5.2 | 20,637 [20,271–20,973] | 24.804 [24.402–25.248] | 47.822 [46.706–49.284] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 15,379 [14,957–15,806] | 33.295 [32.378–34.215] | 67.718 [64.194–70.175] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Direct service | 983.056 [983.037–983.065] | 0.391 [0.381–0.409] | 0.611 [0.556–0.682] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 983.037 [983.033–983.045] | 0.613 [0.575–0.643] | 0.869 [0.793–0.955] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Praxis core v0.5.2 | 983.036 [983.031–983.040] | 0.565 [0.548–0.590] | 0.830 [0.788–0.910] | 0.000 [0.000–0.000] errors/run |
| 16384 B content, 512 connections, 1000 RPS | Praxis core nightly-20261002 | 983.048 [983.036–983.056] | 0.628 [0.614–0.642] | 0.909 [0.871–0.974] | 0.000 [0.000–0.000] errors/run |

## nighthawk

| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |
| --- | --- | ---: | ---: | ---: | --- |
| 0 B content, 16 connections, 1000 RPS | Direct service | 1,000 [1,000–1,000] | 0.182 [0.177–0.191] | 0.277 [0.256–0.316] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 0 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 999.989 [999.966–1,000] | 0.380 [0.365–0.389] | 0.529 [0.477–0.588] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 0 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 1,000 [1000.000–1,000] | 0.337 [0.309–0.364] | 0.481 [0.420–0.558] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 0 B content, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 1,000 [1000.000–1,000] | 0.386 [0.374–0.406] | 0.546 [0.516–0.592] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 16384 B content, 16 connections, 1000 RPS | Direct service | 1000.000 [1000.000–1,000] | 0.275 [0.261–0.295] | 0.471 [0.426–0.561] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 16384 B content, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 1000.000 [999.999–1,000] | 0.506 [0.472–0.528] | 0.715 [0.652–0.786] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 16384 B content, 16 connections, 1000 RPS | Praxis core v0.5.2 | 1000.000 [1000.000–1,000] | 0.440 [0.423–0.474] | 0.671 [0.623–0.757] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 0.000 [0.000–0.000] |
| 16384 B content, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 999.966 [999.966–999.966] | 0.500 [0.471–0.535] | 0.737 [0.676–0.838] † | non-2xx 0.000 [0.000–0.000]; resets 0.000 [0.000–0.000]; in flight at cutoff 1.000 [1.000–1.000] |

† Nighthawk reports the nearest quantile at or above p99; the exact percentile is retained per run. In-flight requests at cutoff are distinct from confirmed failures.
