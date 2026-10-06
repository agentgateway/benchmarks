# Standalone common forwarding: AI matrix

Values are arithmetic means of three runs followed by [minimum–maximum].
Latency p99 is the mean of each run's p99, **not a pooled p99**. RPS counts successful
responses. Fortio latency includes all response statuses. Do not compare different
workloads, traffic rates, APIs or deployment profiles as if they were equal work.
Every individual pass and raw artifact path is in [load-rows.json](../data/load-rows.json).

## fortio

| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |
| --- | --- | ---: | ---: | ---: | --- |
| anthropic / 1024 B content, 32 connections, unlimited | Direct service | 59,954 [59,574–60,206] | 0.533 [0.531–0.537] | 1.987 [1.983–1.994] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 22,506 [21,949–23,208] | 1.422 [1.378–1.457] | 2.684 [2.612–2.761] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, unlimited | Praxis core v0.5.2 | 28,881 [28,311–29,823] | 1.108 [1.072–1.130] | 2.447 [2.407–2.527] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 21,948 [21,603–22,284] | 1.458 [1.435–1.481] | 2.817 [2.786–2.840] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Direct service | 998.936 [998.928–998.945] | 0.332 [0.317–0.349] | 0.512 [0.507–0.516] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.924 [998.919–998.933] | 0.558 [0.502–0.608] | 0.801 [0.723–0.886] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Praxis core v0.5.2 | 998.935 [998.923–998.947] | 0.556 [0.535–0.598] | 0.820 [0.788–0.884] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 998.933 [998.920–998.946] | 0.572 [0.539–0.607] | 0.813 [0.769–0.883] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.318 [0.312–0.321] | 0.577 [0.567–0.585] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.488 [0.451–0.529] | 0.751 [0.691–0.830] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Praxis core v0.5.2 | 2,999 [2,999–2,999] | 0.485 [0.447–0.538] | 0.775 [0.699–0.879] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 2,999 [2,999–2,999] | 0.486 [0.454–0.521] | 0.744 [0.688–0.817] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Direct service | 10,363 [10,175–10,624] | 3.088 [3.011–3.144] | 15.137 [14.976–15.256] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 10,414 [10,170–10,698] | 3.073 [2.990–3.146] | 9.030 [8.420–9.543] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Praxis core v0.5.2 | 9,577 [9,442–9,683] | 3.341 [3.304–3.388] | 7.129 [7.044–7.209] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 9,641 [9,565–9,715] | 3.319 [3.293–3.345] | 10.197 [9.759–11.058] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Direct service | 998.934 [998.914–998.948] | 0.635 [0.614–0.662] | 1.577 [1.317–1.725] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.924 [998.899–998.938] | 0.951 [0.892–1.006] | 1.960 [1.937–1.978] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Praxis core v0.5.2 | 998.915 [998.903–998.922] | 1.069 [1.034–1.110] | 1.985 [1.981–1.989] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 998.924 [998.901–998.935] | 0.916 [0.875–0.965] | 1.947 [1.925–1.970] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.629 [0.615–0.645] | 1.696 [1.650–1.755] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.907 [0.866–0.975] | 1.952 [1.940–1.973] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Praxis core v0.5.2 | 2,999 [2,999–2,999] | 1.093 [1.068–1.132] | 1.987 [1.985–1.989] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 2,999 [2,999–2,999] | 0.878 [0.852–0.917] | 1.945 [1.933–1.961] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Direct service | 58,129 [56,663–59,010] | 0.550 [0.542–0.564] | 2.036 [1.988–2.126] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 22,646 [22,423–22,998] | 1.413 [1.391–1.427] | 2.668 [2.633–2.710] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Praxis core v0.5.2 | 27,450 [27,151–27,667] | 1.165 [1.156–1.178] | 2.492 [2.457–2.530] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 20,780 [20,487–21,182] | 1.540 [1.510–1.561] | 2.898 [2.880–2.911] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Direct service | 998.948 [998.945–998.951] | 0.336 [0.322–0.344] | 0.510 [0.476–0.556] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.940 [998.936–998.944] | 0.560 [0.521–0.596] | 0.806 [0.763–0.868] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Praxis core v0.5.2 | 998.943 [998.941–998.945] | 0.505 [0.480–0.525] | 0.741 [0.684–0.792] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 998.934 [998.921–998.942] | 0.568 [0.558–0.586] | 0.812 [0.787–0.861] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.316 [0.310–0.320] | 0.584 [0.578–0.595] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.478 [0.444–0.504] | 0.738 [0.681–0.794] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Praxis core v0.5.2 | 2,999 [2,999–2,999] | 0.434 [0.404–0.461] | 0.685 [0.625–0.743] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 2,999 [2,999–2,999] | 0.482 [0.471–0.497] | 0.734 [0.703–0.780] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Direct service | 70,302 [69,459–71,788] | 7.282 [7.130–7.369] | 25.126 [25.032–25.290] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 19,291 [18,758–19,701] | 26.544 [25.979–27.286] | 40.627 [39.784–42.237] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Praxis core v0.5.2 | 22,263 [21,916–22,503] | 22.992 [22.745–23.352] | 48.369 [47.334–49.252] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 17,339 [16,674–17,684] | 29.539 [28.942–30.693] | 56.683 [49.062–64.974] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Direct service | 10,115 [9,971–10,387] | 3.164 [3.080–3.208] | 15.799 [15.633–15.886] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 10,207 [9,910–10,508] | 3.136 [3.044–3.228] | 9.272 [8.811–9.623] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Praxis core v0.5.2 | 9,411 [9,336–9,457] | 3.399 [3.383–3.427] | 7.358 [7.277–7.402] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 9,430 [9,409–9,462] | 3.393 [3.381–3.400] | 10.799 [9.932–12.501] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Direct service | 998.941 [998.934–998.946] | 0.647 [0.634–0.666] | 1.717 [1.693–1.752] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.932 [998.929–998.937] | 0.932 [0.885–0.965] | 1.955 [1.935–1.969] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Praxis core v0.5.2 | 998.918 [998.903–998.926] | 1.045 [1.019–1.062] | 1.982 [1.979–1.984] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 998.925 [998.903–998.939] | 0.929 [0.904–0.967] | 1.955 [1.945–1.970] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.621 [0.619–0.622] | 1.665 [1.643–1.703] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.894 [0.838–0.937] | 1.948 [1.923–1.967] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Praxis core v0.5.2 | 2,999 [2,999–2,999] | 1.070 [1.043–1.088] | 1.984 [1.981–1.986] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 2,999 [2,999–2,999] | 0.878 [0.840–0.915] | 1.945 [1.928–1.962] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Direct service | 14,341 [14,183–14,532] | 35.671 [35.198–36.068] | 1,076 [935.413–1,210] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 11,654 [11,488–11,934] | 43.919 [42.880–44.543] | 186.755 [178.194–199.208] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Praxis core v0.5.2 | 8,857 [8,720–8,931] | 57.764 [57.286–58.664] | 101.774 [99.679–105.829] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 10,433 [10,174–10,582] | 49.060 [48.358–50.289] | 90.395 [88.416–93.123] | 0.000 [0.000–0.000] errors/run |

## aiperf

| Case | Treatment | Successful RPS | Mean TTFT ms | p99 TTFT ms | Mean ITL ms | Errors per run |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| anthropic, 16 streams | Direct service | 41.230 [41.152–41.296] | 26.483 [26.462–26.521] | 28.354 [28.112–28.790] | 5.573 [5.552–5.585] | 0.000 [0.000–0.000] |
| anthropic, 16 streams | Agentgateway v1.6.0 | 41.304 [41.180–41.430] | 27.073 [26.981–27.147] | 29.169 [29.092–29.249] | 5.566 [5.545–5.586] | 0.000 [0.000–0.000] |
| anthropic, 16 streams | Praxis core v0.5.2 | 41.192 [41.162–41.211] | 27.609 [27.561–27.672] | 31.690 [31.398–31.942] | 5.569 [5.563–5.579] | 0.000 [0.000–0.000] |
| anthropic, 16 streams | Praxis core nightly-20261002 | 41.100 [40.909–41.257] | 26.846 [26.809–26.879] | 28.853 [28.630–28.983] | 5.593 [5.578–5.608] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Direct service | 324.371 [324.188–324.663] | 27.233 [27.152–27.291] | 36.871 [35.925–37.488] | 5.603 [5.599–5.609] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Agentgateway v1.6.0 | 324.014 [323.813–324.284] | 27.661 [27.502–27.829] | 37.744 [37.326–38.535] | 5.599 [5.594–5.603] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Praxis core v0.5.2 | 286.487 [282.032–289.400] | 41.182 [40.547–42.372] | 88.814 [87.321–90.260] | 5.723 [5.711–5.742] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Praxis core nightly-20261002 | 323.837 [323.578–324.073] | 27.549 [27.517–27.594] | 36.688 [36.109–37.110] | 5.606 [5.603–5.608] | 0.000 [0.000–0.000] |
| openai, 16 streams | Direct service | 41.344 [41.179–41.450] | 26.326 [26.309–26.337] | 27.366 [27.235–27.448] | 5.590 [5.576–5.616] | 0.000 [0.000–0.000] |
| openai, 16 streams | Agentgateway v1.6.0 | 41.308 [41.250–41.400] | 26.655 [26.593–26.762] | 27.916 [27.730–28.282] | 5.588 [5.576–5.599] | 0.000 [0.000–0.000] |
| openai, 16 streams | Praxis core v0.5.2 | 41.184 [41.167–41.206] | 27.383 [27.366–27.405] | 30.490 [30.246–30.904] | 5.591 [5.590–5.592] | 0.000 [0.000–0.000] |
| openai, 16 streams | Praxis core nightly-20261002 | 41.247 [41.126–41.377] | 26.632 [26.591–26.679] | 27.537 [27.389–27.660] | 5.600 [5.584–5.617] | 0.000 [0.000–0.000] |
| openai, 128 streams | Direct service | 323.328 [322.052–324.551] | 26.891 [26.851–26.957] | 33.511 [32.443–34.471] | 5.662 [5.638–5.687] | 0.000 [0.000–0.000] |
| openai, 128 streams | Agentgateway v1.6.0 | 320.843 [320.436–321.462] | 27.191 [27.086–27.358] | 33.938 [33.076–34.394] | 5.707 [5.692–5.723] | 0.000 [0.000–0.000] |
| openai, 128 streams | Praxis core v0.5.2 | 318.745 [315.616–321.503] | 31.139 [30.357–32.177] | 57.582 [55.127–60.646] | 5.611 [5.593–5.629] | 0.000 [0.000–0.000] |
| openai, 128 streams | Praxis core nightly-20261002 | 322.359 [321.797–322.779] | 27.164 [27.131–27.223] | 34.063 [33.728–34.398] | 5.672 [5.669–5.679] | 0.000 [0.000–0.000] |
